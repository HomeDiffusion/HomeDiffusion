# Home Diffusion Dockerfile
# LICENSE: DISTRIBUTED UNDER GPL 3.0 
# REPOSITORY: https://github.com/HomeDiffusion/HomeDiffusion/
# AUTHOR: https://github.com/DesignsByVanessa
# DEMO: https://www.homes.org/home-diffusion/get-started/

FROM continuumio/miniconda3
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app

# Create the environment:
COPY environment.yml .
RUN conda env create -f environment.yml
RUN echo "source activate env" > ~/.bashrc
SHELL ["conda", "run", "-n", "homeDiffusion", "/bin/bash", "-c"]

COPY ./src /app/src
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "homeDiffusion", "python", "src/home_diffusion.py"]
