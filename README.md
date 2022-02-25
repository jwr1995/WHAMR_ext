# Generating the WHAMR_ext dataset

## Python requirements

See WHAMR website for original requirements: http://wham.whisper.ai/

## Prerequisites

This requires the wsj0 (https://catalog.ldc.upenn.edu/LDC93S6A/) dataset,
and the WHAM noise corpus available here (*http://wham.whisper.ai/*).

## Creating WHAMR_ext

Copy and merge the content of this repositary with the original WHAMR simulation scripts: https://storage.googleapis.com/whisper-public/whamr_scripts.tar.gz

To re-run the reverb paramater generation
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
Cite the WHAMR paper:

```sh
@inproceedings{Maciejewski2020WHAMR,
    title     = {WHAMR!: Noisy and Reverberant Single-Channel Speech Separation},
    author    = {Maciejewski, Matthew and Wichern, Gordon and Le Roux, Jonathan},
    booktitle = {Proc. IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)},
    year      = {2020},
    month     = may
}
```
