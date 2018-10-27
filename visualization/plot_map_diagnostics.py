import sys
import os
sys.path.append(os.environ['GOTMWORK_ROOT']+'/tools', )
from gotmanalysis import *

timetag = '20080701-20080731'
# timetag = '20090101-20090131'
# casename = 'COREII_Global'
casename = 'JRA55-do_Global'

# diagnostics
# var = 'mld_deltaR_mean'
# levels1 = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 110, 130, 150, 180, 210, 240, 280, 320, 360, 407, 454, 500]
# levels2 = [-90, -75, -60, -45, -30, -25, -20, -15, -10, -5, 0, 5, 10, 15, 20, 25, 30, 45, 60, 75, 90]
var = 'PE_delta'
levels1 = None
levels2 = None

# update data
update_data = False

# paths
s1data_root = os.environ['GOTMRUN_ROOT']+'/'+casename+'/VR1m_DT600s_'+timetag
s2data_root = os.environ['GOTMFIG_ROOT']+'/data/'+casename+'/VR1m_DT600s_'+timetag
fig_root = os.environ['GOTMFIG_ROOT']+'/'+casename+'/VR1m_DT600s_'+timetag
os.makedirs(s2data_root, exist_ok=True)
os.makedirs(fig_root, exist_ok=True)

turbmethod_list = ['KPP-CVMix',
                   'KPP-ROMS',
                   'KPPLT-EFACTOR',
                   'KPPLT-ENTR',
                   'KPPLT-RWHGK',
                   'EPBL',
                   'EPBL-LT',
                   'SMC',
                   'SMCLT',
                   'K-EPSILON-SG',
                   'OSMOSIS']
legend_list = ['KPP-CVMix',
               'KPP-ROMS',
               'KPPLT-VR12',
               'KPPLT-LF17',
               'KPPLT-RWHGK16',
               'ePBL',
               'ePBL-LT',
               'SMC-KC94',
               'SMCLT-H15',
               'k-epsilon',
               'OSMOSIS']
nm = len(turbmethod_list)
irow_2col = [1, 2, 0, 1, 2, 3, 3, 4, 4, 5, 5]
icol_2col = [0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1]
labels_2col = ['(b)', '(c)', '(g)', '(h)', '(i)', '(d)', '(j)', '(e)', '(k)','(f)','(l)']

# get diagnostics
for i in np.arange(nm):
    tmname = turbmethod_list[i]
    print(tmname)
    basepath = s1data_root+'/'+tmname
    s2data_name = s2data_root+'/data_'+var+'_'+tmname+'.npz'
    figname = fig_root+'/fig_'+var+'.png'
    loclist = sorted(os.listdir(basepath))
    if update_data or not os.path.isfile(s2data_name):
        # save data
        pathlist = [basepath+'/'+x+'/gotm_out_s1.nc' for x in loclist]
        godmobj = GOTMOutputDataMap(pathlist)
        gmobj = godmobj.diagnostics(var)
        gmobj.save(s2data_name)
    else:
        # read data
        gmobj = GOTMMap().load(s2data_name)
    if i == 0:
        nloc = len(loclist)
        darr = np.zeros([nm, nloc])
        lon = gmobj.lon
        lat = gmobj.lat
        name = gmobj.name
        units = gmobj.units
    darr[i,:] = gmobj.data

# forcing regime
tmname = 'KPP-CVMix'
basepath = s1data_root+'/'+tmname
s2data_name = s2data_root+'/data_forcing_regime_'+tmname+'.npz'
if update_data or not os.path.isfile(s2data_name):
    # save data
    loclist = sorted(os.listdir(basepath))
    pathlist = [basepath+'/'+x+'/gotm_out_s1.nc' for x in loclist]
    godmobj = GOTMOutputDataMap(pathlist)
    forcing_regime = np.zeros(godmobj.ncase)
    unstable = np.zeros(godmobj.ncase)
    for i in np.arange(godmobj.ncase):
        if np.mod(i, 100) == 0:
            print('{:6.2f} %'.format(i/godmobj.ncase*100.0))
        tmp = GOTMOutputData(godmobj._paths[i], init_time_location=False)
        forcing_regime[i] = tmp.diag_forcing_regime_BG12()

    gmobj_fr = GOTMMap(data=forcing_regime, lon=godmobj.lon, lat=godmobj.lat, name='forcing_regime')
    gmobj_fr.save(s2data_name)
else:
    # read data
    gmobj_fr = GOTMMap().load(s2data_name)

# create figure
nrow = (nm+2)//2
fig_width = 12
fig_height = 3+2*(nrow-1)

# plot figure
height_ratios = [1]*nrow
height_ratios.append(0.15)
width_ratios = [1, 1, 0.05]
f, axarr = plt.subplots(nrow, 2, sharex='col')
f.set_size_inches(fig_width, fig_height)

for i in np.arange(nm):
    # plot figure
    n = icol_2col[i]
    m = irow_2col[i]
    if i == 0:
        gmdata = darr[i,:]
        gmobj = GOTMMap(data=gmdata, lon=lon, lat=lat, name=name, units=units)
        im1 = gmobj.plot(axis=axarr[m,n], levels=levels1, add_colorbar=False)
    else:
        gmdata = darr[i,:] - darr[0,:]
        gmobj = GOTMMap(data=gmdata, lon=lon, lat=lat, name=name, units=units)
        im2 = gmobj.plot(axis=axarr[m,n], levels=levels2, add_colorbar=False, cmap='RdBu_r')
    axarr[m,n].text(0.02, 0.94, labels_2col[i]+' '+legend_list[i], transform=axarr[m,n].transAxes,
                     fontsize=12, color='white', fontweight='bold', va='top')

# standard deviation
# dstd = np.std(darr, axis=0)
# gmobj = GOTMMap(data=dstd, lon=lon, lat=lat, name=name, units=units)
# im0 = gmobj.plot(axis=axarr[0,0], add_colorbar=False, cmap='viridis', vmax=vmax0, vmin=vmin0)
# axarr[0,0].text(0.02, 0.94, '(a) STD', transform=axarr[0,0].transAxes,
#                      fontsize=12, color='white', fontweight='bold', va='top')

# forcing regime
im0 = plot_forcing_regime(gmobj_fr, axis=axarr[0,0], add_colorbar=False)
axarr[0,0].text(0.02, 0.94, '(a) Forcing regime', transform=axarr[0,0].transAxes,
                     fontsize=12, color='white', fontweight='bold', va='top')

# reduce margin
plt.tight_layout()

# colorbar
plt.subplots_adjust(right=0.95)
cax0 = plt.axes([0.85, 0.7, 0.1, 0.25])
cax0.set_visible(False)
cb_ticks = [1, 2, 3, 4, 5, 6, 7, 8]
cb_ticks_labels = ['S', 'L', 'C', 'SL', 'SC', 'LC', 'SLC', 'NA']
cb0 = plt.colorbar(im0, ax=cax0, ticks=cb_ticks)
cb0.ax.set_yticklabels(cb_ticks_labels)
# cb0.formatter.set_powerlimits((-2, 2))
# cb0.update_ticks()
cax1 = plt.axes([0.85, 0.37, 0.1, 0.25])
cax1.set_visible(False)
cb1 = plt.colorbar(im1, ax=cax1)
cb1.formatter.set_powerlimits((-2, 3))
cb1.update_ticks()
cax2 = plt.axes([0.85, 0.04, 0.1, 0.25])
cax2.set_visible(False)
cb2 = plt.colorbar(im2, ax=cax2)
cb2.formatter.set_powerlimits((-3, 3))
cb2.update_ticks()

# save figure
plt.savefig(figname, dpi = 300)
