import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from os import path

import sys

def main(fname, log_thresh=-0.07):
	print 'loading', fname+'.'

	img=mpimg.imread(path.join('.', fname))
	arr = np.asarray(img)
	width_in_pixels, height_in_pixels, number_of_planes =  arr.shape

	## Calculate the ratio between red and green channels.
	## Note:  avoid division by zero error by adding 1/255 ( = 0.0039) to both planes
	r_g = (arr[:, :, 0] + 0.0039)/(arr[:, :, 1] + 0.0039) 

	## Calculate luminosity of each pixel
	# https://stackoverflow.com/questions/6442118/python-measuring-pixel-brightness
	luminosity = (0.2126*arr[:, :, 0]) + (0.7152*arr[:, :, 1]) + (0.0722*arr[:, :, 2])

	## Convert luminosity values to a grayscale image by stacking four planes (RGBA).
	grayscale = np.dstack((luminosity, luminosity, luminosity, np.ones(luminosity.shape)))

	## Find pixel indices to convert to grayscale
	indices = r_g >= log_thresh

	## Replacee pixels above the threshold with ghe grayscale pixels.
	arr[indices] = grayscale[indices]


	## Output the final processed image.
	fig = plt.figure()
	plt.imshow(arr)
	plt.subplots_adjust(left=0, right=1., bottom=0, top=1.)
	fig.set_size_inches(width_in_pixels/400., height_in_pixels/400.)
	fig.savefig(path.join('.', fname+ ' - live_dead_filter.png'), dpi=400.)

def test_params(input_file='sample_input.png', log_thresh=-0.07, test_range=0.20):

	## Read in an input image.
	img=mpimg.imread(path.join('.', input_file))
	arr = np.asarray(img)

	## Write a file reproducing the input image.
	fig = plt.figure()
	plt.imshow(arr)
	cbar = plt.colorbar() # Create a colorbar for equivalent spacing with other plots.
	cbar.remove() # But then remove it because scale is not relevant for this plot.
	fig = resize_labels(fig)
	fig.savefig(path.join('.', 'unprocessed.png'), dpi=400)

	## Show a representation of the pixel intensities for each of the three channels.
	for c, channel in enumerate(['red', 'green', 'blue']):
		if channel == 'red':
			cmap = 'Reds'
		elif channel == 'blue':
			cmap = 'Blues'
		elif channel == 'green':
			cmap = 'Greens'

		fig = plt.figure()
		plt.imshow(arr[:,:,c], cmap=cmap, vmin=0, vmax=1.)
		cbar = plt.colorbar()
		cbar.set_ticks([0, 0.25, 0.5, 0.75, 1.0])
		fig = resize_labels(fig)

		fig.savefig(path.join('.', 'single channel - '+channel+'.png'), dpi=400)

	## Calculate the ratio between red and green channels.
	## Note:  avoid division by zero error by adding 1/255 to numerator and denominator.
	r_g = (arr[:, :, 0]+.0039)/(arr[:, :, 1]+.0039) 

	## Take the logarithm of the ratio as the threshold value.
	r_g_log = np.log10(r_g)

	## Plot a histogram of the r_g values
	fig = plt.figure()
	plt.hist(r_g_log.flatten(), bins=100)
	ax = plt.gca()
	ax.set_xlabel('log10(r/g)')
	ax.set_ylabel('# of pixels in bin')
	fig.savefig(path.join('.', 'r_g histogram.png'), dpi=400)

	## Show a representation of the r_g values on either side of the threshold.
	low_bound = log_thresh - test_range/2.
	high_bound = log_thresh + test_range/2.
	fig = plt.figure()
	plt.imshow(r_g_log, cmap='Greys', vmin=low_bound, vmax=high_bound)

	cbar = plt.colorbar()
	#cbar.set_label('log10(r/g)')
	cbar.set_ticks([low_bound, thresh, high_bound])


	fig = resize_labels(fig)
	fig.set_size_inches(3.8, 3.0)
	plt.subplots_adjust(left=0.05, right=0.85)
	fig.savefig(path.join('.', 'ratio threshold - r_g.png'), dpi=400)


	## Calculate luminosity of each pixel
	# https://stackoverflow.com/questions/6442118/python-measuring-pixel-brightness
	luminosity = (0.2126*arr[:, :, 0]) + (0.7152*arr[:, :, 1]) + (0.0722*arr[:, :, 2])

	fig = plt.figure()
	plt.imshow(luminosity, cmap='Greys_r', vmin=0., vmax=1.0)
	fig = resize_labels(fig)
	fig.savefig(path.join('.', 'luminosity-based grayscale.png'), dpi=400)

	## Convert luminosity values to a grayscale image by stacking four planes (RGBA).
	grayscale = np.dstack((luminosity, luminosity, luminosity, np.ones(luminosity.shape)))

	## Find pixel indices to convert to grayscale
	indices = r_g_log >= thresh

	## Replacee pixels above the threshold with the grayscale pixels.
	arr[indices] = grayscale[indices]

	## Output the final processed image.
	fig = plt.figure()
	plt.imshow(arr)
	cbar = plt.colorbar() # Create a colorbar for equivalent spacing with other plots.
	cbar.remove() # But then remove it because scale is not relevant for this plot.
	fig = resize_labels(fig)
	fig.savefig(path.join('.', 'output.png'), dpi=400)

def resize_labels(fig):
	for a, ax in enumerate(fig.get_axes()):
		if a == 0:
			## Hide tick labels for main plot.
			ax.set_xticks([])
			ax.set_yticks([])
		else:
			## Increase label size for colorbar axis.
			ax.tick_params(labelsize=16)
	fig.set_size_inches(3.7, 3.)
	return fig



if __name__ == '__main__':

	args = sys.argv

	if len(args) == 1:
		print 'Please specify a file to use as input. e.g. "python live_dead_filter.py input.png"'

	else:

		if args[1] == 'test_params':
			param_list = args[2:]
			errors = False

			if len(param_list)%2 != 0: ## i.e. odd number of entries in parameter list.
				print 'Expecting a sequence of [param_name] [value] pairs as arguments.'
				errors = True
			else:
				## Initialize with default parameters ...
				input_file, thresh, test_range = ('sample_input.png', -0.07, 0.20) 
				param_pairs = []
				n_params = len(param_list)/2

				## ... but replace default parameters where present in the argument list
				for p in range(n_params):

					p_name, value = param_list[2*p:2*p+2]
					
					if p_name == 'input': input_file = value
					elif p_name == 'thresh': thresh = float(value)
					elif p_name == 'test_range': test_range = float(value)
					else: errors = True

			if not errors:
				test_params(input_file=input_file, log_thresh=thresh, test_range=test_range)
			else:
				print 'Error in parameter entry.  Please consult the README.'

		elif len(args) in [4, 2]:
			if len(args) == 4:
				fname, pname, value = args[1:]
				if pname == 'thresh':
					main(fname, log_thresh=float(value))
				else:
					print 'Could not understand arguments. Please consult the README.'
				
			elif len(args) == 2:
				pf = '.'
				fname = args[1]
				main(fname)

		else:
			print 'Could not understand arguments. Please consult the README.' 

