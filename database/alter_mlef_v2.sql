USE forensic_dept_db;

ALTER TABLE mlef_records
ADD COLUMN has_bite BOOLEAN DEFAULT FALSE AFTER has_burn,
ADD COLUMN has_dislocation BOOLEAN DEFAULT FALSE AFTER has_bite,
ADD COLUMN has_explosive_inj BOOLEAN DEFAULT FALSE AFTER has_dislocation,
ADD COLUMN internal_injuries TEXT AFTER other_injuries;

ALTER TABLE mlef_records
ADD COLUMN weapon_firearm BOOLEAN DEFAULT FALSE AFTER weapon_blunt,
ADD COLUMN weapon_explosive BOOLEAN DEFAULT FALSE AFTER weapon_firearm;

ALTER TABLE mlef_records
ADD COLUMN is_life_endangering BOOLEAN DEFAULT FALSE AFTER category_of_hurt;

ALTER TABLE mlef_records
ADD COLUMN drugs_consumed BOOLEAN DEFAULT FALSE AFTER alcohol_consumed;

ALTER TABLE mlef_records
ADD COLUMN sa_history TEXT AFTER accompanying_officer_info,
ADD COLUMN sa_vaginal_penetration BOOLEAN DEFAULT FALSE AFTER sa_history,
ADD COLUMN sa_anal_penetration BOOLEAN DEFAULT FALSE AFTER sa_vaginal_penetration,
ADD COLUMN sa_inter_labial_penetration BOOLEAN DEFAULT FALSE AFTER sa_anal_penetration;

ALTER TABLE mlef_records
ADD COLUMN mlef_investigations TEXT AFTER sa_inter_labial_penetration,
ADD COLUMN mlef_referrals TEXT AFTER mlef_investigations,
ADD COLUMN mlef_other_opinions TEXT AFTER mlef_referrals;
