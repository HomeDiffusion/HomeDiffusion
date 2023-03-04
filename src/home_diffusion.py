"""
LICENSE: DISTRIBUTED UNDER GPL 3.0 
REPOSITORY: https://github.com/HomeDiffusion/HomeDiffusion/
AUTHOR: https://github.com/DesignsByVanessa
OVERVIEW: https://www.homes.org/home-diffusion/
DEMO: https://www.homes.org/home-diffusion/get-started/
"""

import random

import cv2
import einops
import gradio as gr
import numpy as np
import torch
from pytorch_lightning import seed_everything

import config
from annotator.mlsd import MLSDdetector
from annotator.util import HWC3, resize_image
from cldm.ddim_hacked import DDIMSampler
from cldm.model import create_model, load_state_dict

apply_mlsd = MLSDdetector()

model = create_model('./models/cldm_v15.yaml').cpu()
model.load_state_dict(load_state_dict('./models/control_sd15_mlsd.pth', location='cuda'))
model = model.cuda()
ddim_sampler = DDIMSampler(model)


def process(input_image, prompt, scene_type, design_inspirations, a_prompt, n_prompt, num_samples, image_resolution, detect_resolution, ddim_steps, guess_mode, strength, scale, seed, eta, value_threshold, distance_threshold):
    with torch.no_grad():
        input_image = HWC3(input_image)
        detected_map = apply_mlsd(resize_image(input_image, detect_resolution), value_threshold, distance_threshold)
        detected_map = HWC3(detected_map)
        img = resize_image(input_image, image_resolution)
        H, W, C = img.shape

        detected_map = cv2.resize(detected_map, (W, H), interpolation=cv2.INTER_NEAREST)

        control = torch.from_numpy(detected_map.copy()).float().cuda() / 255.0
        control = torch.stack([control for _ in range(num_samples)], dim=0)
        control = einops.rearrange(control, 'b h w c -> b c h w').clone()

        if seed == -1:
            seed = random.randint(0, 65535)
        seed_everything(seed)

        if config.save_memory:
            model.low_vram_shift(is_diffusing=False)

        design_inspirations_str = ', '.join(design_inspirations)
        
        crossattn_list = [scene_type + ', ' + prompt + ', ' + a_prompt + ', ' + design_inspirations_str] * num_samples
        cond = {"c_concat": [control], "c_crossattn": [model.get_learned_conditioning(crossattn_list)]}
        un_cond = {"c_concat": None if guess_mode else [control], "c_crossattn": [model.get_learned_conditioning([n_prompt] * num_samples)]}
        shape = (4, H // 8, W // 8)

        if config.save_memory:
            model.low_vram_shift(is_diffusing=True)

        model.control_scales = [strength * (0.825 ** float(12 - i)) for i in range(13)] if guess_mode else ([strength] * 13)  # Magic number. IDK why. Perhaps because 0.825**12<0.01 but 0.826**12>0.01
        samples, intermediates = ddim_sampler.sample(ddim_steps, num_samples,
                                                     shape, cond, verbose=False, eta=eta,
                                                     unconditional_guidance_scale=scale,
                                                     unconditional_conditioning=un_cond)

        if config.save_memory:
            model.low_vram_shift(is_diffusing=False)

        x_samples = model.decode_first_stage(samples)
        x_samples = (einops.rearrange(x_samples, 'b c h w -> b h w c') * 127.5 + 127.5).cpu().numpy().clip(0, 255).astype(np.uint8)

        results = [x_samples[i] for i in range(num_samples)]
    return [255 - cv2.dilate(detected_map, np.ones(shape=(3, 3), dtype=np.uint8), iterations=1)] + results


block = gr.Blocks().queue()
with block:
    with gr.Row():
        gr.Markdown("## [Home Diffusion](https://www.homes.org/home-diffusion)")
        gr.Markdown("### Like this? [Star us on Github](https://github.com/HomeDiffusion/HomeDiffusion/)")
    with gr.Row():
        gr.Markdown("### Upload a photo of your home and we will inspire you with new ideas!\n")
    with gr.Row():
        gr.Markdown("The photo should be clear of people, pets, personal items, and other distractions.")
    with gr.Row():
        with gr.Column():
            input_image = gr.Image(source='upload', type="numpy")
            prompt = gr.Textbox(label="Prompt")
            scene_type = gr.Dropdown(["Exterior Home Photo", "Kitchen", "Bathroom", "Bedroom", "Living Room", "Dining Room", "Office", "Other"], label="Photo Scene")
            design_inspirations = gr.CheckboxGroup(["Luxury", "Villa", "Mansion", "Ranch Home", "Tropical", "Modern", "Urban", "Warm", "Inviting", "Pool", "Stainless Steel Appliances"], label="Design Inspirations", value=["Luxury", "Modern"])
            run_button = gr.Button(label="Run")
            with gr.Accordion("Advanced options", open=False):
                num_samples = gr.Slider(label="Images", minimum=1, maximum=12, value=4, step=1)
                image_resolution = gr.Slider(label="Image Resolution", minimum=256, maximum=768, value=320, step=64)
                strength = gr.Slider(label="Control Strength", minimum=0.0, maximum=2.0, value=1.3, step=0.01)
                guess_mode = gr.Checkbox(label='Guess Mode', value=False)
                detect_resolution = gr.Slider(label="Hough Resolution", minimum=128, maximum=1024, value=320, step=1)
                value_threshold = gr.Slider(label="Hough value threshold (MLSD)", minimum=0.01, maximum=2.0, value=0.02, step=0.01)
                distance_threshold = gr.Slider(label="Hough distance threshold (MLSD)", minimum=0.01, maximum=20.0, value=0.04, step=0.01)
                ddim_steps = gr.Slider(label="Steps", minimum=1, maximum=100, value=30, step=1)
                scale = gr.Slider(label="Guidance Scale", minimum=0.1, maximum=30.0, value=7.0, step=0.1)
                seed = gr.Slider(label="Seed", minimum=-1, maximum=2147483647, step=1, randomize=True)
                eta = gr.Number(label="eta (DDIM)", value=0.0)
                a_prompt = gr.Textbox(label="Added Prompt", value='')
                n_prompt = gr.Textbox(label="Negative Prompt",
                                      value='low quality, blurry, anime, cartoon, fake, unrealistic, distorted, low light, ugly, unclear')
        with gr.Column():
            result_gallery = gr.Gallery(label='Output', show_label=False, elem_id="gallery").style(grid=2, height='auto')
    ips = [input_image, prompt, scene_type, design_inspirations, a_prompt, n_prompt, num_samples, image_resolution, detect_resolution, ddim_steps, guess_mode, strength, scale, seed, eta, value_threshold, distance_threshold]
    run_button.click(fn=process, inputs=ips, outputs=[result_gallery], api_name="design")


block.launch(server_name='0.0.0.0')
