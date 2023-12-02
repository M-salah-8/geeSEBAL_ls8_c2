### new
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.image as mpimg
import ee
import geopandas as gpd
import pandas as pd
import os
import datetime
import urllib.request
from IPython.display import Image as Iamge_IPy

# export images as tif
def export_image(img, description, folder, aoi):
    # Export cloud-optimized GeoTIFF images
    ee.batch.Export.image.toDrive(**{
        'image': img,
        'description': description,
        'scale': 30,
        "folder": folder,
        'region': aoi,
        'fileFormat': 'GeoTIFF',
        'maxPixels': 3784216672400,
        'formatOptions': {
            'cloudOptimized': True
        }
    }).start()

def export_to_drive(result_img, date, folder, aoi):  ### fix date (but outside fun)
    export_image(
        result_img.image.select(['R','GR','B']).multiply(0.0000275).add(-0.2),  ### check
        "RBG_" + date,
        folder,
        aoi
    )

    export_image(
        result_img.image.select('NDVI'),
        "ndvi_" + date,
        folder,
        aoi
    )

    export_image(
        result_img.image.select('ET_24h'),
        "ET_" + date,
        folder,
        aoi
    )

##########################################################################################################

def export_png_images(image, data, data_name, folder, date, aoi):
    if data == 'NDVI':
        URL_img=image.image.select('NDVI').getThumbURL({
        'min': 0,
        'max': 1,
        'palette':['FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718',
                    '74A901', '66A000', '529400', '3E8601','023B01', '012E01', '011D01', '011301'],
        'region': aoi,
        'dimensions': 500,
        'format': 'jpg'
        })
    elif data == 'ET_24h':
        URL_img=image.image.select('ET_24h').getThumbURL({
        'min': 0,
        'max': 10,
        'palette':['deac9c', 'EDD9A6', 'f2dc8d', 'fff199', 'b5e684', '3BB369', '20998F', '25b1c1', '16678A', '114982'],
        'region': aoi,
        'dimensions': 500,
        'format': 'jpg'
        })
    elif data == 'ET_ETp':
        URL_img=image.image.select('ET_ETp').getThumbURL({
        'min': 0,
        'max': 200,
        'palette': ['A52A2A', 'FF8000', '80FF00', '00FF00', '00FF00', '00FF00', '00FF00', '00FF00', '00FF00'],
        'region': aoi,
        'dimensions': 500,
        'format': 'jpg'
        })  
    elif data == 'RGB':
        URL_img=image.image.select(['R','GR','B']).multiply(0.0000275).add(-0.2).getThumbURL({
        'min': 0,
        'max': 0.3,
        'gamma': 1.5,
        'region': aoi,
        'dimensions': 500,
        'format': 'jpg'
        }) 

    download_dr = os.path.join(folder, 'images', 'raw')
    if not os.path.isdir(download_dr):
        os.makedirs(download_dr)

    download_dr = os.path.join(download_dr, f'{data_name}_{date}.jpg')

    urllib.request.urlretrieve(URL_img, download_dr)

##############################################################

# export spreadsheets function
def write_reducers_to_excel(result_img, eta_df, etp_df, ndvi_df, kc_dates_df, date, aoi_field):
    reducers = [ee.Reducer.max(), ee.Reducer.mean(), ee.Reducer.stdDev(), ee.Reducer.min()]
    eta_stats = []
    etp_stats = []
    ndvi_stats = []
    for i in range(len(reducers)):
            stat = result_img.image.select('NDVI','ET_24h', 'ETp').reduceRegion(
                    reducer = reducers[i],
                    geometry = aoi_field,
                    scale = 30,
                    maxPixels = 9e14
                    )
            stat_dic = stat.getInfo()
            eta_stats.append(stat_dic['ET_24h'])
            ndvi_stats.append(stat_dic['NDVI'])
            etp_stats.append(stat_dic['ETp'])
    kc = kc_dates_df.loc[kc_dates_df['date'] == date,'kc'].values[0]
    et_row = {'date': date, 'max': eta_stats[0], 'mean': eta_stats[1], 'stdDev': eta_stats[2], 'min': eta_stats[3]}
    etp_row = {'date': date, 'mean': etp_stats[1], 'kc':kc, 'kc*ETp':kc*etp_stats[1]}
    ndvi_row = {'date': date, 'max': ndvi_stats[0], 'mean': ndvi_stats[1], 'stdDev': ndvi_stats[2], 'min': ndvi_stats[3]}
    eta_df.loc[len(eta_df)] = et_row
    etp_df.loc[len(etp_df)] = etp_row
    ndvi_df.loc[len(ndvi_df)] = ndvi_row

###########################################################################

def images_plt_layout(folder, data_name):
    raw_dr = os.path.join(folder, 'images', 'raw')
    raw_images = [os.path.join(raw_dr, f) for f in os.listdir(raw_dr)]

    data_colors = {
        'NDVI': ['FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718',
                '74A901', '66A000', '529400', '3E8601','023B01', '012E01', '011D01', '011301'],
        'ETa': ['deac9c', 'EDD9A6', 'f2dc8d', 'fff199', 'b5e684', '3BB369', '20998F', '25b1c1', '16678A', '114982'],
        'ETa_ETp': ['A52A2A', 'FF8000', '80FF00', '00FF00', '00FF00', '00FF00', '00FF00', '00FF00', '00FF00']
    }

    data_lim = {
        'NDVI': {'min': 0, 'max': 1},
        'ETa': {'min': 0, 'max': 8},
        'ETa_ETp': {'min': 0, 'max': 200}
    }
    for raw_image in raw_images:

        raw = mpimg.imread(raw_image)

        # color pallet
        colors_hex = data_colors[data_name]
        colors_rgb = [tuple(int(color.lstrip('#')[i:i+2],16)/255.0 for i in (0,2,4)) for color in colors_hex]
        custom_cmap = LinearSegmentedColormap.from_list('custom_colormap', colors_rgb, N = 256)

        plt.figure(figsize=(5,6))
        plt.figure(facecolor='white')
        plt.imshow(raw, cmap = custom_cmap, vmin = data_lim[data_name]['min'], vmax = data_lim[data_name]['max'])
        plt.axis('off')
        plt.colorbar()
        plt.title(os.path.basename(raw_image).split('.')[0])
        
        ex_dr = os.path.join(folder, 'images', 'layout')
        if not os.path.isdir(ex_dr):
            os.makedirs(ex_dr)
        plt.savefig(os.path.join(ex_dr, os.path.basename(raw_image)), bbox_inches = 'tight', pad_inches = 0.1)
        # plt.show()

##############################################################

def image_combination(folder, data_name):
    layout_dr = folder
    layout_images = [os.path.join(layout_dr, f) for f in os.listdir(layout_dr)]

    img_num = len(layout_images)
    if img_num > 3:
        rows = 2
        cols = round(img_num/2 + 0.2)
        fig, axes = plt.subplots(rows,cols, figsize = (23.4,7.8))
    else:
        rows = 1
        cols = img_num
        fig, axes = plt.subplots(rows,cols, figsize = (23.4,7.8))

    for idx, layout_image in enumerate(layout_images):
        row = idx // cols
        col = idx % cols
        file_name = os.path.basename(layout_image).split('.')[0]
        
        img = mpimg.imread(layout_image)
        if rows > 1:
            axes[row,col].imshow(img)
            axes[row,col].axis('off')

        else:
            axes[col].imshow(img)
            axes[col].axis('off')


    plt.tight_layout()
    # plt.show

    save_dr = os.path.join(folder, 'images')
    plt.savefig(layout_dr + f'combination_{data_name}.png', bbox_inches = 'tight', pad_inches = 0.1)

#########################################################################

# export charts
def save_plot_maxmeanmin(df, chart_name, folder):
    plt.figure(figsize=(9,5.8))
    plt.figure(facecolor='gray')
    colors = {'max':'green', 'stdDev': 'yellow', 'mean': 'blue', 'min':'red'}

    for column in ['max', 'mean', 'min']:
        plt.plot([datetime.datetime.strptime(date, '%Y-%m-%d') for date in df['date']], df[column], marker= 'o' , color= colors[column], linestyle = '-',linewidth= 2, markersize=8)

    plt.title(chart_name)
    plt.xticks(rotation=90)
    plt.xlabel('date')
    plt.ylabel(chart_name)
    plt.grid(True)
    plt.legend(['max', 'mean', 'min'], loc= 'best')
    file_name = '_'.join(chart_name.split(' '))

    c_dr = os.path.join(folder, 'charts')
    if not os.path.isdir(c_dr):
            os.makedirs(c_dr)
    plt.savefig(c_dr + '\\maxmeanmin vs date.png', bbox_inches = 'tight', pad_inches = 0.1)

    # plt.show()

def save_plot_et_etp (eta_sheet_df, etp_sheet_df, chart_name, folder):
    
    df = pd.DataFrame({
      'date': eta_sheet_df['date'],
      'ETa_mean': eta_sheet_df['mean'],
      'ETp_mean': etp_sheet_df['mean'],
      'kc*ETp': etp_sheet_df['kc*ETp']
    })
    plt.figure(figsize=(9,5.8))
    plt.figure(facecolor='gray')
    colors = {'kc*ETp':'blue', 'ETa_mean': 'green'}

    for column in ['kc*ETp', 'ETa_mean']:
        plt.plot([datetime.datetime.strptime(date, '%Y-%m-%d') for date in df['date']], df[column], marker= 'o' , color= colors[column], linestyle = '-',linewidth= 2, markersize=8)

    plt.title(chart_name)
    plt.xticks(rotation=90)
    plt.xlabel('date')
    plt.ylabel(chart_name)
    plt.grid(True)
    plt.legend(['kc*ETp', 'ETa_mean'], loc= 'best')
    file_name = '_'.join(chart_name.split(' '))

    c_dr = os.path.join(folder, 'charts')
    if not os.path.isdir(c_dr):
            os.makedirs(c_dr)
    plt.savefig(c_dr + '\\ET ETp mm day vs date.png', bbox_inches = 'tight', pad_inches = 0.1)

########################################################################################

# save shp to image
def shapefile_image(project_shp, field_shp, folder):
    plt.figure(figsize=(9,7))
    ax = project_shp.plot(color= 'white', edgecolor= 'black')
    field_shp.plot(ax=ax, color= 'green', edgecolor= 'black')
    plt.savefig(os.path.join(folder,'shpimage.png'), bbox_inches = 'tight', pad_inches = 0)

##################################################################################

# export prief
def export_priefs(season_dr, et_folder, ndvi_folder):
    img_a1 = os.path.join(season_dr, 'shpimage.png')
    img_a2 = os.path.join(ndvi_folder, 'charts', 'maxmeanmin vs date.png')
    img_a3 = os.path.join(et_folder, 'ETa', 'charts', 'maxmeanmin vs date.png')
    img_a4 = os.path.join(et_folder, 'ETa_ETp', 'charts', 'ET ETp mm day vs date.png')

    img_b1 = os.path.join(ndvi_folder, 'images', 'layoutcombination_NDVI.png')
    img_b2 = os.path.join(et_folder, 'ETa', 'images', 'layoutcombination_ETa.png')
    img_b3 = os.path.join(et_folder, 'ETa_ETp', 'images', 'layoutcombination_ETa_ETp.png')


    lay_imgs = [plt.imread(i) for i in [img_a1, img_a2, img_a3, img_a4]]
    # fig, axs = plt.subplots(1,2)
    fig, axs = plt.subplots(4,1,  figsize= (16.5,16.2))

    for i,ax in enumerate(axs.flat):
        if i < len(lay_imgs):
            # ig = plt.imread(lay_imgs[i])
            ax.imshow(lay_imgs[i])
        ax.axis('off')

    plt.tight_layout()
    plt.savefig(os.path.join(season_dr,'charts.png'), bbox_inches = 'tight', pad_inches = 0)

    lay_imgs = [plt.imread(i) for i in [img_b1, img_b2, img_b3]]
    fig, axs = plt.subplots(3,1,  figsize= (12,15.6))

    for i,ax in enumerate(axs.flat):
        if i < len(lay_imgs):
            ax.imshow(lay_imgs[i])
        ax.axis('off')

    plt.tight_layout()
    plt.savefig(os.path.join(season_dr,'layouts.png'), bbox_inches = 'tight', pad_inches = 0)

    fig, axs = plt.subplots(1,2, figsize= (33,32.4),gridspec_kw={'width_ratios':[1,3]}, facecolor='white')
    lay_imgs = [plt.imread(os.path.join(season_dr,'charts.png')), plt.imread(os.path.join(season_dr,'layouts.png'))]
    for i,ax in enumerate(axs.flat):
        if i < len(lay_imgs):
            ax.imshow(lay_imgs[i])
        ax.axis('off')

    plt.savefig(os.path.join(season_dr,'brief.png'), bbox_inches = 'tight', pad_inches = 0)