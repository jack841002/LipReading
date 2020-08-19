import csv
import os

import editdistance
import numpy as np
from keras.callbacks import Callback
from keras.utils import Sequence
from keras.preprocessing.text import Tokenizer
import difflib
from os.path import join
import pickle

# from common.files import make_dir_if_not_exists
# from core.decoding.decoder import Decoder
# from core.model.lipnet import LipNet
from wer import wer_sentence
import pkuseg
seg = pkuseg.pkuseg()   #以默认配置加载模型


class WordErrorRate(Callback):

	def __init__(self, lipnet, val_generator: Sequence, decoder, samples: int = 8):
		super().__init__()

		# self.output_path = output_path
		self.lipnet     = lipnet
		self.generator   = val_generator.__getitem__
		self.decoder     = decoder
		self.samples     = samples
		self.tok_path = join('split_data', 'vocabulary_tok.pickle')
		with open(self.tok_path, 'rb') as handle:
			self.tok = pickle.load(handle)


	def get_sample_batch(self) -> list:
		sample_batch  = []
		generator_idx = 0
		samples_left  = self.samples
		batch_label = []
		batch_label_length = []

		while samples_left > 0:
			batch = self.generator(generator_idx)[0]
			#samples_to_take = min(batch['the_input'], samples_left)
			batch_input = batch['the_input']

			samples_to_take = min(len(batch_input), samples_left)

			if samples_to_take <= 0:
				break

			y_pred       = self.lipnet.predict(batch['the_input'][0:samples_to_take])
			input_length = batch['input_length'][0:samples_to_take]

			decoded = self.decoder.decode(y_pred, input_length)

			for i in range(0, samples_to_take):
				sample_batch.append(decoded[i])
				batch_label.append(batch['the_labels'][i])
				batch_label_length.append(batch['label_length'][i])

			samples_left  -= samples_to_take
			generator_idx += 1

		return sample_batch, batch_label, batch_label_length

	def GetEditDistance(self, str1, str2):
	    leven_cost = 0
	    s = difflib.SequenceMatcher(None, str1, str2)
	    for tag, i1, i2, j1, j2 in s.get_opcodes():
	        #print('{:7} a[{}: {}] --> b[{}: {}] {} --> {}'.format(tag, i1, i2, j1, j2, str1[i1: i2], str2[j1: j2]))
	        if tag == 'replace':
	            leven_cost += max(i2-i1, j2-j1)
	        elif tag == 'insert':
	            leven_cost += (j2-j1)
	        elif tag == 'delete':
	            leven_cost += (i2-i1)
	    return leven_cost

	# @staticmethod
	# def calculate_mean_generic(data: [tuple], mean_length: float, evaluator) -> (float, float):
	#	values = [float(evaluator(x[0], x[1])) for x in data]

	#	total = 0.0
	#	total_norm = 0.0
	#	#mean_length = float(mean_length)

	#	for v in values:
	#		total += v
	#		total_norm += v / mean_length

	#	length = len(data)
	#	return total / length, total_norm / length

	def labels_to_text(self, label):
		label = list(label[label>0])
		words = self.tok.sequences_to_texts([label])
		text = words[0].replace(" ", "")
		return(text)

	def calculate_wer(self, data: [tuple], label: [tuple], label_length: [tuple]) -> float:
		# print(data)
		# mean_length = np.mean([len(d[1].split()) for d in data])
		words_num = 0
		word_error_num = 0

		for i in range(len(data)):
			word_edit_distance = chinese_wer_sentence(str(data[i]), str(label[i]))
			words_num = words_num + label_length[i]

			if(word_edit_distance <= label_length[i]):
				word_error_num += word_edit_distance
			else:
				word_error_num += label_length[i]

		return (word_error_num / words_num) * 100
		#return self.calculate_mean_generic(data, mean_length, wer_sentence)


	def calculate_cer(self, data: [tuple], label: [tuple], label_length: [tuple]) -> float:
		# print(data)
		# mean_length = np.mean([len(d[1]) for d in data])
		cha_num = 0
		cha_error_num = 0

		for i in range(len(data)):
			cha_edit_distance = self.GetEditDistance(str(data[i]), str(label[i]))
			cha_num = cha_num + label_length[i]

			if(cha_edit_distance <= label_length[i]):
				cha_error_num += cha_edit_distance
			else:
				cha_error_num += label_length[i]

		return (cha_error_num / cha_num) * 100
		#return self.calculate_mean_generic(data, mean_length, editdistance.eval)


	def calculate_statistics(self) -> dict:
		sample_batch, batch_label, batch_label_length = self.get_sample_batch()
		batch_text = []
		batch_word_len = []

		for i in batch_label:
			text = self.labels_to_text(i)
			batch_text.append(text)
			batch_word_len.append(len(seg.cut(text)))
		print('sample_batch', sample_batch)
		print('batch_text:', batch_text)
		print('batch_word_len', batch_word_len)
		print('batch_label_length', batch_label_length)

		wer = self.calculate_wer(sample_batch, batch_text, batch_word_len)
		cer = self.calculate_cer(sample_batch, batch_text, batch_label_length)

		return {
			'samples':  len(sample_batch),
			'wer':      wer,
			#'wer_norm': wer_norm,
			'cer':      cer,
			#'cer_norm': cer_norm
		}


	'''def on_train_begin(self, logs=None):
		output_dir = os.path.dirname(self.output_path)
		make_dir_if_not_exists(output_dir)

		with open(self.output_path, 'w') as f:
			writer = csv.writer(f)
			writer.writerow(['epoch', 'samples', 'wer', 'wer_norm', 'cer', 'cer_norm'])'''


	def on_epoch_end(self, epoch: int, logs=None):
		print('Epoch {:05d}: Calculating error rates...'.format(epoch + 1), end='')

		statistics = self.calculate_statistics()

		print('\rEpoch {:05d}: ({} samples) [WER {:.3f}]\t[CER {:.3f}]\n'.format(epoch + 1, statistics['samples'], statistics['wer'], statistics['cer']))

		'''with open(self.output_path, 'a') as f:
			writer = csv.writer(f)
			writer.writerow([
				epoch,
				statistics['samples'],
				statistics['wer'],
				statistics['wer_norm'],
				statistics['cer'],
				statistics['cer_norm']
			])'''
