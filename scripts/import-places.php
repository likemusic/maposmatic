<?php

$db = pg_connect("host=gis-db user=maposmatic password=secret dbname=gis options='--client_encoding=UTF8'");

pg_query($db, "DROP TABLE IF EXISTS place") or die("ooops");

pg_query($db, "CREATE TABLE place (
  name varchar(200) DEFAULT NULL,
  alternative_names text DEFAULT NULL,
  osm_type varchar(100) NOT NULL,
  osm_id bigint NOT NULL,
  class varchar(100) DEFAULT NULL,
  type varchar(100) DEFAULT NULL,
  lon float DEFAULT NULL,
  lat float DEFAULT NULL,
  place_rank float DEFAULT NULL,
  importance float DEFAULT NULL,
  country_code varchar(10) DEFAULT NULL,
  display_name varchar(1000) DEFAULT NULL,
  west float DEFAULT NULL,
  south float DEFAULT NULL,
  east float DEFAULT NULL,
  north float DEFAULT NULL,
  PRIMARY KEY (osm_type,osm_id)
)") or die("ooops2");

pg_query($db, "CREATE INDEX ON place(name)") or die("ooops3");
pg_query($db, "BEGIN") or die("ooops4");


$ignore_columns = ['street','city','county','state','country','city','wikidata','wikipedia','housenumbers'];

$ignore_classes = ['class','highway','waterway','natural','landuse','water','river','residential','stream','reservoir','residential,secondary,tertiary','primary','track','tertiary','unclassified','trunk','primary,secondary','secondary,tertiary','service','path','footway','cycleway','drain','ditch'];

$fp = fopen("planet-latest_geonames.tsv", "r");

$columns = preg_split('|\t|', trim(fgets($fp)));

$n = 0; $i = 0;

while (!feof($fp)) {
    if (++$n % 1000 == 0) {
        echo number_format($n)." ".number_format($i)."\r";
        pg_query($db, "COMMIT");
        pg_query($db, "BEGIN");
    }
    $line = trim(fgets($fp));
    if (empty($line)) {
        // echo "empty line\n";
        continue;
    }
    $row = [];

    $cols = preg_split('|\t|', $line);

    if (isset($cols[24])) {
        // echo "line too long\n";
        continue;
    }
    
    foreach ($cols as $key => $val) {
        switch($columns[$key]) {
        case 'name':
        case 'alternative_names':
        case 'osm_type':
        case 'class':
        case 'type':
        case 'country_code':
        case 'display_name':
            $row[$columns[$key]] = pg_escape_literal($db, $val);
            break;
        case 'osm_id':
        case 'place_rank':
        case 'importance':
        case 'lat':
        case 'lon':
        case 'west':
        case 'east':
        case 'north':
        case 'south':
            if (empty($val)) $val = 0;
            if ($val == "NaN") $val = "NULL";
            $row[$columns[$key]] = $val;
            break;
        }
    }

    if (!isset($row['class'])) {
        // echo "no class\n";
        continue;
    }
    if (in_array(substr($row['class'],1,-1), $ignore_classes)) {
        // echo "ignoring class\n";
        continue;
    }

    if (strstr($row['type'], ",")) {
        // echo "comma in type\n";
        continue;
    }
    
    foreach ($ignore_columns as $key) {
        unset($row[$key]);
    }

    if (empty($row['place_rank'])) $row['place_rank'] = 0.0;
    if (empty($row['importance'])) $row['importance'] = 0.0;

    $query = "INSERT INTO place (" . join(",", array_keys($row)) . ") VALUES (" . join(",", $row) .  ");";

    if (!pg_query($db, $query)) {
        echo "$query\n";
        echo pg_last_error($db)."\n\n";
        exit;
    }

    $i++;
}

echo "COMMIT\n";
pg_query($db, "COMMIT") or die("ooops6");
