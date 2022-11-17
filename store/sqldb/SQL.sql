select count(*) from contract_data;
select * from contract_data;
select count(*) from seed_data;
select * from seed_data where type='users';
select count(*) from training_data;
select count(*) from training_data where type = 'seed';