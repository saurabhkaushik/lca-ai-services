SET SQL_SAFE_UPDATES = 0;

update lca_dev.seed_data set keywords='' WHERE id is not null;
delete from lca_dev.training_data where type='seed';

delete from lca_dev.training_data where type='contract';
