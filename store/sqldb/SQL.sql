select count(*) from contract_data;
select * from contract_data;

select count(*) from seed_data;
select * from seed_data where domain = 'esg';

select * from training_data where domain = 'esg';
select count(*) from training_data where type = 'contract';

