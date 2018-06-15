import numpy as np
from da.tca import TCA
#from linear_mmd import get_mmd
import pandas as pd

basedir = '/shared/tale2/Shared/szhou/openfmri/preprocessed/whole'

def sample_selection(data_matrix, labels, size):
    np.random.seed(seed=144)
    np.random.shuffle(data_matrix)
    return data_matrix[:size,:], labels[:size]

def extract_domain_data(data,labels,domain,size=0):
    n_samples = len(labels)
    ds1 = []
    label_ds1 = []
    ds2 = []
    label_ds2 = []
    for i in range(n_samples):
        if labels[i]==domain[0]:
            ds1.append(data[i])
            label_ds1.append(domain[0])
        if labels[i]==domain[1]:
            ds2.append(data[i])
            label_ds2.append(domain[1])
    ds1 = np.array(ds1)
    ds2 = np.array(ds2)
    label_ds1 = np.array(label_ds1)
    label_ds2 = np.array(label_ds2)
    if size!=0:
        ds1, label_ds1 = sample_selection(ds1, label_ds1, size)
        ds2, label_ds2 = sample_selection(ds2, label_ds2, size)

    return np.vstack((ds1,ds2)), np.hstack((label_ds1, label_ds2))

def get_src_domains(tar_domain):
    
    task_ids = [1,2,3,4,5,6,8,9,10,21,22]
    src_domain_pool = list(set(task_ids) - set(tar_domain))
    src_list = []
    src_domains = []
    for i in range(len(src_domain_pool)-1):
        for j in range (i+1,len(src_domain_pool)):
            src_domains.append([src_domain_pool[i],src_domain_pool[j]])
            src_list.append('%s_%s'%(src_domain_pool[i],src_domain_pool[j]))
    return src_domains, src_list

def main():
    data_run1=np.load('%s/zstat_run1.npy'%basedir)
    data_run2=np.load('%s/zstat_run2.npy'%basedir)
    data = np.hstack((data_run1,data_run2))

    data = data.T
    labels_run1=np.loadtxt('%s/data_key_run1.txt'%basedir)[:,0]
    labels_run2=np.loadtxt('%s/data_key_run2.txt'%basedir)[:,0]
    labels = np.hstack((labels_run1,labels_run2))

    n_samples = len(labels)

    # change dimension and target domain labels here
    tc_dim = 100
    tar_domain = [3,6]


    tar_data, tar_labels = extract_domain_data(data, labels, tar_domain)
    tar_num = len(tar_labels)

    src_domains, src_list = get_src_domains(tar_domain)
    for src_domain in src_domains:
        src_data, src_labels = extract_domain_data(data, labels, src_domain)
        src_num = len(src_labels)

        my_tca = TCA(n_components=tc_dim,kernel='linear')
        src_tca, tar_tca = my_tca.fit_transform(src_data, tar_data)

        tc_to_save = np.vstack((src_tca,tar_tca))
        label_to_save = np.hstack((src_labels,tar_labels))
        label_to_save = label_to_save.reshape((src_num+tar_num,1))
        data_to_save = np.hstack((tc_to_save,label_to_save))
        np.save('%s/TCA_/%sd_tar%s_%ssrc%s_%s.npy'%(basedir, tc_dim,tar_domain[0],
                tar_domain[1],src_domain[0],src_domain[1]),data_to_save)
        #np.save('TCA_trans_matrices/%sd_tar%s_%ssrc%s_%s.npy'%(tc_dim,tar_domain[0],tar_domain[1],src_domain[0],src_domain[1]),V)


if __name__ == '__main__':
    main()
