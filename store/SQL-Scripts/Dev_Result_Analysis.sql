select count(*) from lca_dev.seed_data where domain ='esg'; 
select count(*) from lca_dev.contract_data where domain='esg';
select count(*) from lca_dev.training_data where domain='esg' and type ='seed';
select count(*) from lca_dev.training_data where domain='esg' and type = 'contract';
select count(*) from lca_dev.seed_data where domain ='liabilities';
select count(*) from lca_dev.contract_data where domain='liabilities';
select count(*) from lca_dev.training_data where domain='liabilities' and type ='seed';
select count(*) from lca_dev.training_data where domain='liabilities' and type = 'contract';
