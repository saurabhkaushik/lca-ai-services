select count(*) from contract_data;
select * from contract_data where id ='1da3f1fd-fdbe-4719-8f8d-497722fd13bb';

select count(*) from seed_data;
select * from seed_data where domain = 'esg';

select * from training_data where domain = 'esg';
select count(*) from training_data where type = 'contract';

SELECT * from seed_data where domain='liabilities';



