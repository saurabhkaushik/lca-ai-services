SET SQL_SAFE_UPDATES = 0;

# Keyword Cleanup 
update lca_dev.seed_data set keywords='' WHERE id is not null;

# Training Data Cleanup 
select id, title from lca_dev.contract_data;
delete from lca_dev.contract_data WHERE id is not null;

delete from lca_dev.training_data WHERE id is not null;
delete from lca_dev.training_data where type='seed';
delete from lca_dev.training_data where type='contract';
