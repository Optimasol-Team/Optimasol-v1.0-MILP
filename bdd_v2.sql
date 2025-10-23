CREATE TABLE clients (
    client_id INT PRIMARY KEY AUTO_INCREMENT,
    nom VARCHAR(100),
    email VARCHAR(150),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    tilt DECIMAL(8,2),
    azimuth DECIMAL(8,2),
    router_id VARCHAR(50)
);

CREATE TABLE chauffe_eaux (
    chauffe_eau_id INT PRIMARY KEY AUTO_INCREMENT,
    client_id INT,
    capacite_litres INT,
    puissance_kw DECIMAL(5,2),
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
);

CREATE TABLE donnees_meteo (
    meteo_id INT PRIMARY KEY AUTO_INCREMENT,
    client_id INT,
    temperature_ext DECIMAL(5,2),
    humidity DECIMAL(5,2),
    wind_speed DECIMAL(5,2),
    precipitation DECIMAL(5,2),
    cloud_cover INT,
    weather_code VARCHAR(50),
    heure_debut DATETIME,
    heure_fin DATETIME,
    source_meteo VARCHAR(50),
    timestamp_acquisition TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE decisions_temperature (
    prevision_id INT PRIMARY KEY AUTO_INCREMENT,
    chauffe_eau_id INT,
    temperature_predite DECIMAL(5,2),
    heure_prevision DATETIME,
    confidence DECIMAL(4,3),
    timestamp_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modele_utilise VARCHAR(100),
    FOREIGN KEY (chauffe_eau_id) REFERENCES chauffe_eaux(chauffe_eau_id)
);
 
CREATE TABLE system_configuration (
    config_id INT PRIMARY KEY AUTO_INCREMENT,
    client_id INT,
    cold_water_temperature DECIMAL(4,1),
    minimum_comfort_temperature_enabled TINYINT(1),
    minimum_comfort_temperature DECIMAL(4,1),
    contract_type ENUM('base', 'heures_creuses', 'tempo'),
    base_tariff DECIMAL(6,4),
    hp_tariff DECIMAL(6,4),
    hc_tariff DECIMAL(6,4),
    comfort_schedule JSON,
    hot_water_draws JSON,
    off_peak_hours JSON,
    custom_tariffs JSON,
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
);

CREATE TABLE configuration_prediction (
    config_id INT PRIMARY KEY AUTO_INCREMENT,
    chauffe_eau_id INT,
    intervalle_measure_min INT,
    horizon_prediction_heures INT,
    seuil_alerte_basse DECIMAL(5,2),
    seuil_alerte_haute DECIMAL(5,2),
    FOREIGN KEY (chauffe_eau_id) REFERENCES chauffe_eaux(chauffe_eau_id)
);

CREATE TABLE temperatures_reelles (
    mesure_id INT PRIMARY KEY AUTO_INCREMENT,
    chauffe_eau_id INT,
    temperature DECIMAL(5,2),
    timestamp_mesure TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE decision (
    id_decision INT PRIMARY KEY AUTO_INCREMENT,
    chauffe_eau_id INT,
    statut VARCHAR(50),
    heure_decision DATETIME,
    timestamp_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chauffe_eau_id) REFERENCES chauffe_eaux(chauffe_eau_id)
);

CREATE TABLE production_reelle (
    production_id INT PRIMARY KEY AUTO_INCREMENT,
    client_id INT,
    puissance_produite_kw DECIMAL(8,2),
    heure_production DATETIME,
    timestamp_mesure TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
);

CREATE TABLE previsions_production (
    prevision_id INT PRIMARY KEY AUTO_INCREMENT,
    client_id INT,
    puissance_prevue_kw DECIMAL(8,2),
    heure_prevision DATETIME,
    timestamp_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
);