select count(*) from seed_data where domain ='esg';
select count(*) from contract_data where domain='esg';
select count(*) from training_data where domain='esg' and type='seed';
select count(*) from training_data where domain='esg' and type='contract';
select count(*) from seed_data where domain ='liabilities';
select count(*) from contract_data where domain='liabilities';
select count(*) from training_data where domain='liabilities' and type='seed';
select count(*) from training_data where domain='liabilities' and type='contract';
