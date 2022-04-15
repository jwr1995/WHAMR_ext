# Generating the WHAMR_ext dataset

This repository is for creating extended datasets to the WHAMR corpus with larger RT60 values (between 1s and 3s).

Link to our paper: https://arxiv.org/pdf/2204.06439.pdf

## Python requirements

See WHAMR website for original requirements: http://wham.whisper.ai/

## Prerequisites

This requires the wsj0 (https://catalog.ldc.upenn.edu/LDC93S6A/) dataset,
and the WHAM noise corpus available here (*http://wham.whisper.ai/*).

Additional requirements:

```sh
$ pip install pandas
```

## Creating WHAMR_ext

Copy and merge the content of this repositary with the original WHAMR simulation scripts: https://storage.googleapis.com/whisper-public/whamr_scripts.tar.gz

To re-run the reverb paramater generation with a new seed edit data/extended.py and run
```sh
$ cd data
$ python extended.py
$ cd ../
```

To simulate WHAMR_ext:

```sh
$ python create_whamr_ext_from_scratch.py 
    --wsj0-root /path/to/the/wsj/dataset/ 
    --wham-noise-root /path/to/wham_noise/ 
    --output-dir /path/to/output/directory/ 
 
```



## Citation
Please cite the original WHAMR paper:

```sh
@inproceedings{Maciejewski2020WHAMR,
    title     = {WHAMR!: Noisy and Reverberant Single-Channel Speech Separation},
    author    = {Maciejewski, Matthew and Wichern, Gordon and Le Roux, Jonathan},
    booktitle = {Proc. IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)},
    year      = {2020},
    month     = may
}
```

Please also cite our paper:

```sh
@misc{https://doi.org/10.48550/arxiv.2204.06439,
  title = {Receptive Field Analysis of Temporal Convolutional Networks for Monaural Speech Dereverberation},
  author = {Ravenscroft, William and Goetze, Stefan and Hain, Thomas},
  year = {2022},
  month = april,
  doi = {10.48550/ARXIV.2204.06439},
  url = {https://arxiv.org/abs/2204.06439},
  publisher = {arXiv},
  copyright = {Creative Commons Attribution 4.0 International}
}
```

[![PWC](https://img.shields.io/endpoint.svg?url=https://paperswithcode.com/badge/receptive-field-analysis-of-temporal/speech-dereverberation-on-whamr)](https://paperswithcode.com/sota/speech-dereverberation-on-whamr?p=receptive-field-analysis-of-temporal)

[![PWC](https://img.shields.io/endpoint.svg?url=https://paperswithcode.com/badge/receptive-field-analysis-of-temporal/speech-dereverberation-on-whamr-ext)](https://paperswithcode.com/sota/speech-dereverberation-on-whamr-ext?p=receptive-field-analysis-of-temporal)
