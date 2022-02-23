import os
import numpy as np
import soundfile as sf
import pandas as pd
from constants import SAMPLERATE
import argparse
from utils import read_scaled_wav, quantize, fix_length, create_wham_mixes, append_or_truncate
from wham_room import WhamRoom


FILELIST_STUB = os.path.join('data', 'mix_2_spk_filenames_{}.csv')

SINGLE_DIR = 'mix_single'
BOTH_DIR = 'mix_both'
CLEAN_DIR = 'mix_clean'
S1_DIR = 's1'
S2_DIR = 's2'
NOISE_DIR = 'noise'
SUFFIXES = ['_anechoic_ext', '_reverb_ext']

MONO = True  # Generate mono audio, change to false for stereo audio
SPLITS = ['tr','cv','tt']
SAMPLE_RATES = ['16k', '8k'] # Remove element from this list to generate less data
DATA_LEN = ['max', 'min'] # Remove element from this list to generate less data

def create_wham(wsj_root, wham_noise_path, output_root):
    LEFT_CH_IND = 0
    if MONO:
        ch_ind = LEFT_CH_IND
    else:
        ch_ind = [0, 1]

    scaling_npz_stub = os.path.join(wham_noise_path, 'metadata', 'scaling_{}.npz')
    reverb_param_stub = os.path.join('data', 'ext_reverb_params_{}.csv')

    for splt in SPLITS:

        wsjmix_path = FILELIST_STUB.format(splt)
        wsjmix_df = pd.read_csv(wsjmix_path)

        scaling_npz_path = scaling_npz_stub.format(splt)
        scaling_npz = np.load(scaling_npz_path, allow_pickle=True)

        noise_path = os.path.join(wham_noise_path, splt)

        reverb_param_path = reverb_param_stub.format(splt)
        reverb_param_df = pd.read_csv(reverb_param_path)

        for wav_dir in ['wav' + sr for sr in SAMPLE_RATES]:
            for datalen_dir in DATA_LEN:
                output_path = os.path.join(output_root, wav_dir, datalen_dir, splt)
                for sfx in SUFFIXES:
                    os.makedirs(os.path.join(output_path, CLEAN_DIR+sfx), exist_ok=True)
                    os.makedirs(os.path.join(output_path, SINGLE_DIR+sfx), exist_ok=True)
                    os.makedirs(os.path.join(output_path, BOTH_DIR+sfx), exist_ok=True)
                    os.makedirs(os.path.join(output_path, S1_DIR+sfx), exist_ok=True)
                    os.makedirs(os.path.join(output_path, S2_DIR+sfx), exist_ok=True)
                os.makedirs(os.path.join(output_path, NOISE_DIR), exist_ok=True)

        utt_ids = scaling_npz['utterance_id']
        start_samp_16k = scaling_npz['speech_start_sample_16k']

        for i_utt, output_name in enumerate(utt_ids):

            if os.path.exists(os.path.join(output_path, NOISE_DIR, output_name)):
                continue
            
            utt_row = reverb_param_df[reverb_param_df['utterance_id'] == output_name]
            room = WhamRoom([utt_row['room_x'].iloc[0], utt_row['room_y'].iloc[0], utt_row['room_z'].iloc[0]],
                            [[utt_row['micL_x'].iloc[0], utt_row['micL_y'].iloc[0], utt_row['mic_z'].iloc[0]],
                             [utt_row['micR_x'].iloc[0], utt_row['micR_y'].iloc[0], utt_row['mic_z'].iloc[0]]],
                            [utt_row['s1_x'].iloc[0], utt_row['s1_y'].iloc[0], utt_row['s1_z'].iloc[0]],
                            [utt_row['s2_x'].iloc[0], utt_row['s2_y'].iloc[0], utt_row['s2_z'].iloc[0]],
                            utt_row['T60'].iloc[0])
            room.generate_rirs()

            # read the 16kHz unscaled speech files, but make sure to add all 'max' padding to end of utterances
            # for synthesizing all the reverb tails
            utt_row = wsjmix_df[wsjmix_df['output_filename'] == output_name]
            s1_path = os.path.join(wsj_root, utt_row['s1_path'].iloc[0])
            s2_path = os.path.join(wsj_root, utt_row['s2_path'].iloc[0])
            s1_temp = quantize(read_scaled_wav(s1_path, 1))
            s2_temp = quantize(read_scaled_wav(s2_path, 1))
            s1_temp, s2_temp = fix_length(s1_temp, s2_temp, 'max')
            noise_samples_temp = read_scaled_wav(os.path.join(noise_path, output_name), 1)
            s1_temp, s2_temp, noise_samples_temp = append_or_truncate(s1_temp, s2_temp,
                                                                      noise_samples_temp, 'max',
                                                                      start_samp_16k=0)  # don't pad beginning yet

            room.add_audio(s1_temp, s2_temp)

            anechoic = room.generate_audio(anechoic=True, fs=SAMPLE_RATES)
            reverberant = room.generate_audio(fs=SAMPLE_RATES)

            for sr_i, sr_dir in enumerate(SAMPLE_RATES):
                wav_dir = 'wav' + sr_dir
                if sr_dir == '8k':
                    sr = 8000
                    downsample = True
                else:
                    sr = SAMPLERATE
                    downsample = False

                for datalen_dir in DATA_LEN:
                    output_path = os.path.join(output_root, wav_dir, datalen_dir, splt)

                    wsjmix_key = 'scaling_wsjmix_{}_{}'.format(sr_dir, datalen_dir)
                    wham_speech_key = 'scaling_wham_speech_{}_{}'.format(sr_dir, datalen_dir)
                    wham_noise_key = 'scaling_wham_noise_{}_{}'.format(sr_dir, datalen_dir)

                    utt_row = wsjmix_df[wsjmix_df['output_filename'] == output_name]
                    s1_path = os.path.join(wsj_root, utt_row['s1_path'].iloc[0])
                    s2_path = os.path.join(wsj_root, utt_row['s2_path'].iloc[0])

                    s1 = read_scaled_wav(s1_path, scaling_npz[wsjmix_key][i_utt][0], downsample)
                    s1 = quantize(s1) * scaling_npz[wham_speech_key][i_utt]
                    s2 = read_scaled_wav(s2_path, scaling_npz[wsjmix_key][i_utt][1], downsample)
                    s2 = quantize(s2) * scaling_npz[wham_speech_key][i_utt]

                    # Make relative source energy of anechoic sources same with original in mono (left channel) case
                    s1_spatial_scaling = np.sqrt(np.sum(s1 ** 2) / np.sum(anechoic[sr_i][0, LEFT_CH_IND, :] ** 2))
                    s2_spatial_scaling = np.sqrt(np.sum(s2 ** 2) / np.sum(anechoic[sr_i][1, LEFT_CH_IND, :] ** 2))

                    noise_samples_full = read_scaled_wav(os.path.join(noise_path, output_name),
                                                         scaling_npz[wham_noise_key][i_utt],
                                                         downsample_8K=downsample, mono=MONO)
                    if datalen_dir == 'max':
                        out_len = len(noise_samples_full)
                    else:
                        out_len = np.minimum(len(s1), len(s2))

                    s1_anechoic, s2_anechoic = fix_length(anechoic[sr_i][0, ch_ind, :out_len].T * s1_spatial_scaling,
                                                          anechoic[sr_i][1, ch_ind, :out_len].T * s2_spatial_scaling,
                                                          datalen_dir)
                    s1_reverb, s2_reverb = fix_length(reverberant[sr_i][0, ch_ind, :out_len].T * s1_spatial_scaling,
                                                      reverberant[sr_i][1, ch_ind, :out_len].T * s2_spatial_scaling,
                                                      datalen_dir)

                    sources = [(s1_anechoic, s2_anechoic), (s1_reverb, s2_reverb)]
                    for i_sfx, (sfx, source_pair) in enumerate(zip(SUFFIXES, sources)):
                        s1_samples, s2_samples, noise_samples = append_or_truncate(source_pair[0], source_pair[1],
                                                                                   noise_samples_full, datalen_dir,
                                                                                   start_samp_16k[i_utt], downsample)

                        mix_clean, mix_single, mix_both = create_wham_mixes(s1_samples, s2_samples, noise_samples)

                        # write audio
                        samps = [mix_clean, mix_single, mix_both, s1_samples, s2_samples]
                        dirs = [CLEAN_DIR, SINGLE_DIR, BOTH_DIR, S1_DIR, S2_DIR]
                        for dir, samp in zip(dirs, samps):
                            sf.write(os.path.join(output_path, dir+sfx, output_name), samp,
                                     sr, subtype='FLOAT')

                        if i_sfx == 0: # only write noise once as it doesn't change between anechoic and reverberant
                            sf.write(os.path.join(output_path, NOISE_DIR, output_name), noise_samples,
                                     sr, subtype='FLOAT')

            if (i_utt + 1) % 500 == 0:
                print('Completed {} of {} utterances'.format(i_utt + 1, len(wsjmix_df)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', type=str, required=True,
                        help='Output directory for writing wsj0-2mix 8 k Hz and 16 kHz datasets.')
    parser.add_argument('--wsj0-root', type=str, required=True,
                        help='Path to the folder containing wsj0/')
    parser.add_argument('--wham-noise-root', type=str, required=True,
                        help='Path to the downloaded and unzipped wham folder containing metadata/')
    args = parser.parse_args()
    create_wham(args.wsj0_root, args.wham_noise_root, args.output_dir)
