-- infra/mysql/init.sql
CREATE USER 'motoriz_migracao'@'%' IDENTIFIED BY 'migracao_dev';
GRANT ALL PRIVILEGES ON motoriz.* TO 'motoriz_migracao'@'%' WITH GRANT OPTION;
CREATE USER 'motoriz_app'@'%' IDENTIFIED BY 'app_dev';
