FROM continuumio/miniconda3

WORKDIR /app

# Create the environment:
COPY environment.yml .
RUN conda env create -f environment.yml

# Activate the environment, and make sure it's activated:
RUN conda activate myenv
RUN echo "Make sure flask is installed:"
RUN python -c "import flask"

# The code to run when container is started:
COPY run.py .
ENTRYPOINT ["python", "run.py"]
