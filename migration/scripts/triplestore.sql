#
# Copyright(c) 2015-2017 BITPlan GmbH
# 
# http://www.profiwiki.de
#
# Author: Wolfgang Fahl
# 
# Access TO Semantic Mediawiki TripleStore
# 2015-06-10
#   
#  FUNCTION split_str
#  FUNCTION namespace
#  VIEW smw_triples
#  VIEW smw_triples_ns
#
# split_str
#   see http://blog.fedecarg.com/2009/02/22/mysql-split-string-FUNCTION/
#
DROP FUNCTION IF EXISTS split_str;
CREATE FUNCTION split_str(
  x VARCHAR(255),
  delim VARCHAR(12),
  pos INT
)
RETURNS VARCHAR(255)
DETERMINISTIC
NO SQL
SQL SECURITY INVOKER
RETURN REPLACE(SUBSTRING(SUBSTRING_INDEX(x, delim, pos),
       LENGTH(SUBSTRING_INDEX(x, delim, pos -1)) + 1),
       delim, '');
#
# namespace
#   see http://www.mediawiki.org/wiki/Manual:Namespace#Built-in_namespaces
#
DROP FUNCTION IF EXISTS namespace;
CREATE FUNCTION namespace (ns INT)
  RETURNS VARCHAR(512)
  LANGUAGE SQL
  DETERMINISTIC
  CONTAINS SQL
  SQL SECURITY INVOKER
  COMMENT 'Mediawiki NameSpace number to Namespace name conversion '
RETURN CASE ns 
    WHEN -2 THEN 'Media:'
    WHEN -1 THEN 'Special:'
    WHEN 0 THEN ''
    WHEN 1 THEN 'Talk:'
    WHEN 2 THEN 'User:'
    WHEN 3 THEN 'User talk:'
    WHEN 4 THEN 'Project:'
    WHEN 5 THEN 'Project talk:'
    WHEN 6 THEN 'File:'
    WHEN 7 THEN 'File talk:'
    WHEN 8 THEN 'Mediawiki:'
    WHEN 9 THEN 'Mediawiki talk:'
    WHEN 10 THEN 'Template:'
    WHEN 11 THEN 'Template talk:'
    WHEN 12 THEN 'Help:'
    WHEN 13 THEN 'Help talk:'
    WHEN 14 THEN 'Category:'
    WHEN 15 THEN 'Category talk:'
    WHEN 102 THEN 'Property:' 
    WHEN 106 THEN 'Form:'
    WHEN 108 THEN 'Concept:' 
    ELSE ''
    END;
# 
# SMW TRIPlES
#
# creates a VIEW based ON the SQLStore3 TABLES TO simplify the access TO the triple store
# which has been complicated BY the SQLStore3 redesign
# the performance OF the VIEW might be slow FOR big wikis (e.g. more than 1 million triples)
# see https://semantic-mediawiki.org/wiki/Database_tables
# see https://semantic-mediawiki.org/wiki/Help:SQLStore
# see https://semantic-mediawiki.org/wiki/SQLStore_update
# see https://semantic-mediawiki.org/wiki/SMWCon_Fall_2012/Improvements_in_SQLStore3
#
# 
CREATE OR REPLACE 
#   
#
# DEFAULT SQL security IS DEFINER which IS trouble SOME WHEN VIEW IS backed up AND restored ON
# a host WHERE the defining USER IS NOT available
#
# see:
# http://stackoverflow.com/questions/10169960/mysql-error-1449-the-user-specified-as-a-definer-does-not-exist
# USE different security setting
SQL SECURITY INVOKER
# 
VIEW smw_triples AS
  SELECT 
    CAST(sois.smw_title AS CHAR) AS subject,
    CAST(soip.smw_title AS CHAR) AS predicate,
    CAST(sdb.o_blob AS CHAR) AS object,
    'blob' AS TYPE
  FROM 
    smw_di_blob sdb
    JOIN smw_object_ids sois ON sois.smw_id=sdb.s_id
    JOIN smw_object_ids soip ON soip.smw_id=sdb.p_id 
  WHERE 
    sdb.o_blob IS NOT NULL
UNION
  SELECT 
    CAST(sois.smw_title AS CHAR) AS subject,
    CAST(soip.smw_title AS CHAR) AS predicate,
    CAST(sdb.o_hash AS CHAR) AS object,
    'shortblob' AS TYPE
  FROM 
    smw_di_blob sdb
    JOIN smw_object_ids sois ON sois.smw_id=sdb.s_id
    JOIN smw_object_ids soip ON soip.smw_id=sdb.p_id 
  WHERE 
    sdb.o_blob IS NULL
UNION
  SELECT 
    CAST(sois.smw_title AS CHAR) AS subject,
    CAST(soip.smw_title AS CHAR) AS predicate,
    IF (sdb.o_value,'true','false') AS object,
    'bool' AS TYPE
  FROM 
    smw_di_bool sdb
    JOIN smw_object_ids sois ON sois.smw_id=sdb.s_id
    JOIN smw_object_ids soip ON soip.smw_id=sdb.p_id  
UNION
  SELECT 
    CAST(sois.smw_title AS CHAR) AS subject,
    CAST(soip.smw_title AS CHAR) AS predicate,
    sdb.o_sortkey AS object,
    'number' AS TYPE
  FROM 
    smw_di_number sdb
    JOIN smw_object_ids sois ON sois.smw_id=sdb.s_id
    JOIN smw_object_ids soip ON soip.smw_id=sdb.p_id
UNION 
  SELECT 
    CAST(sois.smw_title AS CHAR) AS subject,
    CAST(soip.smw_title AS CHAR) AS predicate,
    CONCAT(
       split_str(CAST(sdb.o_serialized AS CHAR),'/',2),'-',
       split_str(CAST(sdb.o_serialized AS CHAR),'/',3),'-',
       split_str(CAST(sdb.o_serialized AS CHAR),'/',4)
       ) AS object,
    'time' AS TYPE
  FROM 
    smw_di_time sdb
    JOIN smw_object_ids sois ON sois.smw_id=sdb.s_id
    JOIN smw_object_ids soip ON soip.smw_id=sdb.p_id
UNION
  SELECT 
    CAST(sois.smw_title AS CHAR) AS subject,
    CAST(soip.smw_title AS CHAR) AS predicate,
    CAST(sdb.o_serialized AS CHAR) AS object,
    'uri' AS TYPE
  FROM 
    smw_di_uri sdb
    JOIN smw_object_ids sois ON sois.smw_id=sdb.s_id
    JOIN smw_object_ids soip ON soip.smw_id=sdb.p_id
UNION
  SELECT 
    CAST(sois.smw_title AS CHAR) AS subject,
    CAST(soip.smw_title AS CHAR) AS predicate,
    CAST(soio.smw_title AS CHAR) AS object,
    'page' AS TYPE
  FROM 
    smw_di_wikipage sdb
    JOIN smw_object_ids sois ON sois.smw_id=sdb.s_id
    JOIN smw_object_ids soip ON soip.smw_id=sdb.p_id
    JOIN smw_object_ids soio ON soio.smw_id=sdb.o_id;
#
# SMW Triples WITH Namespaces
#
#    
CREATE OR REPLACE 
#   
#
# DEFAULT SQL security IS DEFINER which IS trouble SOME WHEN VIEW IS backed up AND restored ON
# a host WHERE the defining USER IS NOT available
#
# see:
# http://stackoverflow.com/questions/10169960/mysql-error-1449-the-user-specified-as-a-definer-does-not-exist
# USE different security setting
SQL SECURITY INVOKER
# 
VIEW smw_triples_ns AS
  SELECT 
    CONCAT(namespace(sois.smw_namespace),CAST(sois.smw_title AS CHAR),CAST(sois.smw_subobject AS CHAR)) AS subject,
    CONCAT(namespace(soip.smw_namespace),CAST(soip.smw_title AS CHAR),CAST(soip.smw_subobject AS CHAR)) AS predicate,
    CAST(sdb.o_blob AS CHAR) AS object,
    'blob' AS TYPE
  FROM 
    smw_di_blob sdb
    JOIN smw_object_ids sois ON sois.smw_id=sdb.s_id
    JOIN smw_object_ids soip ON soip.smw_id=sdb.p_id 
  WHERE 
    sdb.o_blob IS NOT NULL
UNION
  SELECT 
    CONCAT(namespace(sois.smw_namespace),CAST(sois.smw_title AS CHAR),CAST(sois.smw_subobject AS CHAR)) AS subject,
    CONCAT(namespace(soip.smw_namespace),CAST(soip.smw_title AS CHAR),CAST(soip.smw_subobject AS CHAR)) AS predicate,
    CAST(sdb.o_hash AS CHAR) AS object,
    'shortblob' AS TYPE
  FROM 
    smw_di_blob sdb
    JOIN smw_object_ids sois ON sois.smw_id=sdb.s_id
    JOIN smw_object_ids soip ON soip.smw_id=sdb.p_id 
  WHERE 
    sdb.o_blob IS NULL
UNION
  SELECT 
    CONCAT(namespace(sois.smw_namespace),CAST(sois.smw_title AS CHAR),CAST(sois.smw_subobject AS CHAR)) AS subject,
    CONCAT(namespace(soip.smw_namespace),CAST(soip.smw_title AS CHAR),CAST(soip.smw_subobject AS CHAR)) AS predicate,
    IF (sdb.o_value,'true','false') AS object,
    'bool' AS TYPE
  FROM 
    smw_di_bool sdb
    JOIN smw_object_ids sois ON sois.smw_id=sdb.s_id
    JOIN smw_object_ids soip ON soip.smw_id=sdb.p_id  
UNION
  SELECT 
    CONCAT(namespace(sois.smw_namespace),CAST(sois.smw_title AS CHAR),CAST(sois.smw_subobject AS CHAR)) AS subject,
    CONCAT(namespace(soip.smw_namespace),CAST(soip.smw_title AS CHAR),CAST(soip.smw_subobject AS CHAR)) AS predicate,
    sdb.o_sortkey AS object,
    'number' AS TYPE
  FROM 
    smw_di_number sdb
    JOIN smw_object_ids sois ON sois.smw_id=sdb.s_id
    JOIN smw_object_ids soip ON soip.smw_id=sdb.p_id
UNION 
  SELECT 
    CONCAT(namespace(sois.smw_namespace),CAST(sois.smw_title AS CHAR),CAST(sois.smw_subobject AS CHAR)) AS subject,
    CONCAT(namespace(soip.smw_namespace),CAST(soip.smw_title AS CHAR),CAST(soip.smw_subobject AS CHAR)) AS predicate,
    CONCAT(
       split_str(CAST(sdb.o_serialized AS CHAR),'/',2),'-',
       split_str(CAST(sdb.o_serialized AS CHAR),'/',3),'-',
       split_str(CAST(sdb.o_serialized AS CHAR),'/',4)
       ) AS object,
    'time' AS TYPE
  FROM 
    smw_di_time sdb
    JOIN smw_object_ids sois ON sois.smw_id=sdb.s_id
    JOIN smw_object_ids soip ON soip.smw_id=sdb.p_id
UNION
  SELECT 
    CONCAT(namespace(sois.smw_namespace),CAST(sois.smw_title AS CHAR),CAST(sois.smw_subobject AS CHAR)) AS subject,
    CONCAT(namespace(soip.smw_namespace),CAST(soip.smw_title AS CHAR),CAST(soip.smw_subobject AS CHAR)) AS predicate,
    CAST(sdb.o_serialized AS CHAR) AS object,
    'uri' AS TYPE
  FROM 
    smw_di_uri sdb
    JOIN smw_object_ids sois ON sois.smw_id=sdb.s_id
    JOIN smw_object_ids soip ON soip.smw_id=sdb.p_id
UNION
  SELECT 
    CONCAT(namespace(sois.smw_namespace),CAST(sois.smw_title AS CHAR),CAST(sois.smw_subobject AS CHAR)) AS subject,
    CONCAT(namespace(soip.smw_namespace),CAST(soip.smw_title AS CHAR),CAST(soip.smw_subobject AS CHAR)) AS predicate,
    CONCAT(namespace(soio.smw_namespace),CAST(soio.smw_title AS CHAR),CAST(soio.smw_subobject AS CHAR)) AS object,
    'page' AS TYPE
  FROM 
    smw_di_wikipage sdb
    JOIN smw_object_ids sois ON sois.smw_id=sdb.s_id
    JOIN smw_object_ids soip ON soip.smw_id=sdb.p_id
    JOIN smw_object_ids soio ON soio.smw_id=sdb.o_id;
