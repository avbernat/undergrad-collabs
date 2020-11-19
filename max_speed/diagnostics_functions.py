import numpy as np

def heat_map(deviations, f, heat_map, axs, matrix, filename, bar_title):

    a = np.array(matrix)
    axs = axs.flatten()
    im = axs[f].imshow(a, cmap='viridis', interpolation='nearest') # cmap='hot'

    axs[f].title.set_text(filename + '\nMax-Min=%.2f' %(np.max(matrix)-np.min(matrix)))
    axs[f].set_xticks(np.arange(len(deviations)))
    axs[f].set_yticks(np.arange(len(deviations)))
    axs[f].set_xticklabels(deviations, fontsize=8)
    axs[f].set_yticklabels(deviations, fontsize=8)
    axs[f].set_xlabel("Max Dev Val", fontsize=12)
    axs[f].set_ylabel("Min Dev Val", fontsize=12)

    cbar = heat_map.colorbar(im, ax=axs[f], fraction=0.046, pad=0.03)
    cbar.ax.set_ylabel(bar_title, rotation=-90, va="bottom")
    
    rows, cols = a.shape
    for i in range(rows):
        for j in range(cols):
            text = axs[f].text(j, i, a[i, j], ha="center", va="center", color="w", fontsize=6)
    
