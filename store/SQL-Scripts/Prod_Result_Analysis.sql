select count(*) from lca_prod.seed_data where domain ='esg'; 
select count(*) from lca_prod.contract_data where domain='esg';
select count(*) from lca_prod.training_data where domain='esg' and type='seed';
select count(*) from lca_prod.training_data where domain='esg' and type='contract';
select count(*) from lca_prod.seed_data where domain ='liabilities';
select count(*) from lca_prod.contract_data where domain='liabilities';
select count(*) from lca_prod.training_data where domain='liabilities' and type='seed';
select count(*) from lca_prod.training_data where domain='liabilities' and type='contract';
