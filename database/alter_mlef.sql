USE forensic_dept_db;

-- Modify ENUM for category of hurt
ALTER TABLE mlef_records 
MODIFY category_of_hurt ENUM('Non-grievous', 'Grievous', 'Endangering Life', 'Fatal in ordinary course');

-- Add new injury columns
ALTER TABLE mlef_records
ADD COLUMN has_gunshot BOOLEAN DEFAULT FALSE AFTER has_burn,
ADD COLUMN has_cut BOOLEAN DEFAULT FALSE AFTER has_gunshot,
ADD COLUMN has_no_injury BOOLEAN DEFAULT FALSE AFTER has_cut,
ADD COLUMN other_injuries TEXT AFTER has_no_injury;

-- Add new weapon columns
ALTER TABLE mlef_records
ADD COLUMN weapon_sharp BOOLEAN DEFAULT FALSE AFTER other_injuries,
ADD COLUMN weapon_blunt BOOLEAN DEFAULT FALSE AFTER weapon_sharp,
ADD COLUMN weapon_other TEXT AFTER weapon_blunt;

-- Add new alcohol/drugs columns
ALTER TABLE mlef_records
ADD COLUMN alcohol_smelling BOOLEAN DEFAULT FALSE AFTER under_influence_of_alcohol,
ADD COLUMN alcohol_consumed BOOLEAN DEFAULT FALSE AFTER alcohol_smelling,
ADD COLUMN drugs_under_influence BOOLEAN DEFAULT FALSE AFTER alcohol_consumed,
ADD COLUMN alcohol_drugs_negative BOOLEAN DEFAULT FALSE AFTER drugs_under_influence;
