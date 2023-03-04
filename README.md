# HomeDiffusion
## Disrupting Home Design with Stable Diffusion and ControlNet

HomeDiffusion is an open source project that uses Stable Diffusion and ControlNet to revolutionize the way home design is done. With HomeDiffusion, you can run your own design studio and craft beautiful, unique designs with ease.

## Get Started with HomeDiffusion

HomeDiffusion is easy to use and requires only a GPU to run. Here's what you need to get started:

- A GPU with suggested 12GB of VRAM()
- An internet connection
- HomeDiffusion software

Once you have the necessary hardware and software, you can start designing your dream home with HomeDiffusion.


# HomeDiffusion

HomeDiffusion is an innovative open source project that enables users to create design concepts for their homes. Through a fine-tuned implementation of Stable Diffusion and ControlNet, HomeDiffusion provides users with an intuitive and powerful tool to create dream homes that fit their exact specifications.

## What is HomeDiffusion?

HomeDiffusion is a revolutionary open source project that utilizes Stable Diffusion and ControlNet to create highly accurate and customizable home designs. HomeDiffusion is a powerful tool that allows users to design their own homes with unprecedented accuracy and precision. 

Users can customize every aspect of their home design, from the overall layout and structure to the smallest details. HomeDiffusion also provides users with access to a library of pre-made designs and templates, so they can quickly find the perfect home design for their needs.



## Run locally
You can run your own design studio with Home Diffusion if you have your own GPU.

Either way, the first step is to download the file and place it in ./models.

### Step 1 Clone repo and download model
```bash
git clone git@github.com:HomeDiffusion/HomeDiffusion.git
cd HomeDiffusion
# Download the model, this is ~5.4 GB, so grab a coffee. Thanks to lllyasviel!
wget https://huggingface.co/lllyasviel/ControlNet/resolve/main/models/control_sd15_mlsd.pth  -P models/
```

### Launch with conda
```bash
conda env create -f environment.yaml
conda activate homeDiffusion
```

### Advanced Controls
After running thousands of iterations locally, we have set some sane defaults for you. An advanced user guide is coming soon!


#### Acknowledgements
Thank you to many open source contributors who have made this possible, but especially:
- [Stable Diffusion](https://github.com/CompVis/stable-diffusion)
- [Gradio](https://github.com/gradio-app/gradio)
- [Lyumin Zhang](https://github.com/lllyasviel)