-- Мультиплеерные defines из «Family Historical MP mod» (Arthur).
NDefines.NGame.GAME_SPEED_SECONDS = { 0.5, 0.20, 0.15, 0.05, 0.0 }; -- SPEED 4 IS 0.1 IN VANILLA  game speeds for each level. Must be 5 entries with last one 0 for unbound

NDefines.NGame.LAG_DAYS_FOR_LOWER_SPEED = 100;
NDefines.NGame.LAG_DAYS_FOR_PAUSE = 60;
NDefines.NGame.COMBAT_LOG_MAX_MONTHS = 36 -- WAS 48 | drastically cuts down on save file sizes after WW2 starts and well into barbarossa
NDefines.NGame.MESSAGE_TIMEOUT_DAYS = 14 -- WAS 60 	| less messages lying around at the top of your screen
NDefines.NGame.MISSION_REMOVE_FROM_INTERFACE_DEFAULT = 3 -- Default days before a mission is removed from the interface after having failed or completed
NDefines.NCountry.EVENT_PROCESS_OFFSET = 25 -- Performance enhancer. --TW/WTT
NDefines.NFocus.MAX_SAVED_FOCUS_PROGRESS = 35
NDefines.NBuildings.MAX_SHARED_SLOTS = 40
NDefines.NMilitary.TRAINING_EXPERIENCE_SCALE = 80.0

NDefines.NGame.LAG_DAYS_FOR_LOWER_SPEED = 400 -- these defines are most likely hourly and not daily , rever to 100 and 1 if desyncs during someone lagging for 10 days
NDefines.NGame.LAG_DAYS_FOR_PAUSE = 720
NDefines.NGame.COMBAT_LOG_MAX_MONTHS = 12
NDefines.NGame.AIR_LOG_TIMEOUT_HOURS = 24						-- Vanilla was 24
NDefines.NResistance.GARRISON_LOG_MAX_MONTHS = 0

NDefines.NAir.AIR_WING_XP_LOSS_REDUCTION_OVER_FRIENDLY_TERRITORY_FACTOR = 0     --Reduction on XP loss over friendly territory
NDefines.NAir.AIR_WING_XP_AIR_VS_AIR_COMBAT_GAIN = 0                             --Wings in combat gain extra XP
NDefines.NAir.AIR_WING_XP_GROUND_MISSION_COMPLETED_GAIN = 0                    --Bombers bombing, CAS cassing, NBs nbing, kamikazees kamikazeeing, etc.
NDefines.NAir.AIR_WING_XP_RECON_MISSION_COMPLETED_GAIN = 0                    --recon mission
NDefines.NAir.AIR_WING_XP_LOSS_WHEN_KILLED = 0                                    --if a plane dies, the game assumes that a pilot with this amount of xp died and recalcs average. 
NDefines.NAir.AIR_WING_XP_TRAINING_MAX = 2.0                           --Max average XP achieved with training.
NDefines.NAir.AIR_WING_XP_MAX = 0                                             --Per plane XP.
NDefines.NAir.AIR_WING_XP_LEVELS = { 0 }                         --Experience needed to progress to the next level





NDefines.NCountry.POPULATION_YEARLY_GROWTH_BASE = 0                     -- Removed for game stability/reducing chance of desync

NDefines.NMilitary.ENCIRCLED_DISBAND_MANPOWER_FACTOR = 0;

NDefines.NMilitary.MAX_ARMY_EXPERIENCE = 9999;
NDefines.NMilitary.MAX_NAVY_EXPERIENCE = 9999;
NDefines.NMilitary.MAX_AIR_EXPERIENCE  = 9999;
NDefines.NMilitary.UNIT_LEADER_USE_NONLINEAR_XP_GAIN = false
NDefines.NMilitary.EXPERIENCE_COMBAT_FACTOR = 0 --was 0.25
NDefines.NMilitary.ARMY_EXP_BASE_LEVEL = 1
NDefines.NMilitary.UNIT_EXP_LEVELS = { 0.0, 0.3, 0.75, 0.9 }
NDefines.NCountry.SPECIAL_FORCES_CAP_MIN = 48
NDefines.NMilitary.UNIT_LEADER_ASSIGN_TRAIT_COST = 0
NDefines.NMilitary.BASE_LEADER_TRAIT_GAIN_XP = 0.0001 -- Лок на прочачку генов
NDefines.NCountry.REINFORCEMENT_EQUIPMENT_DELIVERY_SPEED = 0.6
NDefines.NCountry.REINFORCEMENT_MANPOWER_DELIVERY_SPEED = 20
NDefines.NCountry.REINFORCEMENT_MANPOWER_CHUNK = 0.08

NDefines.NMilitary.BASE_DIVISION_SUPPORT_SLOT_COST = 0; --vanilla is 10
NDefines.NMilitary.BASE_DIVISION_BRIGADE_CHANGE_COST = 0; --vanilla is 5
NDefines.NMilitary.BASE_DIVISION_BRIGADE_GROUP_COST = 0; --vanilla is 20

NDefines.NIndustrialOrganisation.DESIGN_TEAM_CHANGE_XP_COST = 0
NDefines.NMilitary.UNIT_EXPERIENCE_PER_COMBAT_HOUR = 0.0005; --vanilla is 0.0001
NDefines.NMilitary.UNIT_EXPERIENCE_PER_TRAINING_DAY = 0.003; --vanilla is 0.0015

NDefines.NProduction.EQUIPMENT_MODULE_ADD_XP_COST = 0.0            -- XP cost for adding a new equipment module in an empty slot when creating an equipment variant.
NDefines.NProduction.EQUIPMENT_MODULE_REPLACE_XP_COST = 0.0        -- XP cost for replacing one equipment module with an unrelated module when creating an equipment variant.
NDefines.NProduction.EQUIPMENT_MODULE_CONVERT_XP_COST = 0.0        -- XP cost for converting one equipment module to a related module when creating an equipment variant.
NDefines.NProduction.EQUIPMENT_MODULE_REMOVE_XP_COST = 0.0         -- XP cost for removing an equipment module and leaving the slot empty when creating an equipment variant.

NDefines.NProduction.MINIMUM_NUMBER_OF_FACTORIES_TAKEN_BY_CONSUMER_GOODS_VALUE = 0		-- The minimum number of factories we have to put on consumer goods, by value.
NDefines.NProduction.MINIMUM_NUMBER_OF_FACTORIES_TAKEN_BY_CONSUMER_GOODS_PERCENT = 0



NDefines.NAI.MAX_VOLUNTEER_ARMY_FRACTION  = 0;	-- теперь размер числа добровольцев не зависит от размера армии
NDefines.NDiplomacy.VOLUNTEERS_PER_TARGET_PROVINCE = 0;
NDefines.NDiplomacy.VOLUNTEERS_PER_COUNTRY_ARMY = 0;-- теперь размер числа добровольцев не зависит от размера армии
NDefines.NDiplomacy.VOLUNTEERS_DIVISIONS_REQUIRED  = 5;	
NDefines.NDiplomacy.BASE_SEND_ATTACHE_COST = 0
NDefines.NDiplomacy.BASE_SEND_ATTACHE_CP_COST = 0.0					
NDefines.NCountry.AIR_VOLUNTEER_PLANES_LIMIT = 4;
NDefines.NCountry.AIR_VOLUNTEER_BASES_CAPACITY_LIMIT = 4;

NDefines.NProduction.LICENSE_EQUIPMENT_UPGRADE_XP_FACTOR = 0;


--NDefines.NMilitary.DEPLOY_TRAINING_MAX_LEVEL = 2;
NDefines.NDeployment.BASE_DEPLOYMENT_TRAINING = 2.75;

NDefines.NMilitary.OUT_OF_SUPPLY_ATTRITION = 0.20;                 -- max attrition when out of supply

NDefines.NProduction.MIN_POSSIBLE_TRAINING_MANPOWER = 10000000;
NDefines.NProduction.BASE_FACTORY_SPEED_NAV = 3.75
NDefines.NProduction.BASE_FACTORY_SPEED_MIL = 4.25
NDefines.NProduction.BASE_LICENSE_IC_COST = 0;
NDefines.NProduction.LICENSE_IC_COST_YEAR_INCREASE = 0;
NDefines.NProduction.DEFAULT_MAX_NAV_FACTORIES_PER_LINE = 25
NDefines.NProduction.FLOATING_HARBOR_MAX_NAV_FACTORIES_PER_LINE = 25
NDefines.NProduction.CONVOY_MAX_NAV_FACTORIES_PER_LINE = 25
NDefines.NProduction.CAPITAL_SHIP_MAX_NAV_FACTORIES_PER_LINE = 15
NDefines.NProduction.MAX_CIV_FACTORIES_PER_LINE = 15

-- RESEARCH_AHEAD_BONUS_FACTOR = 0			-- To which extent AI should care about ahead of time bonuses to research #2
-- RESEARCH_BONUS_FACTOR = 100				                    -- To which extent AI should care about bonuses to research #0.9

NDefines.NDiplomacy.VOLUNTEERS_DIVISIONS_REQUIRED = 0;
NDefines.NDiplomacy.PEACE_SCORE_PER_PASS = 100.0  -- When you pass once you should get enough points to finish the peace deal








NDefines.NCountry.RESISTANCE_STRENGTH_FROM_VP = 0.0
NDefines.NCountry.RESISTANCE_STRENGTH_FROM_NEIGHBORS = 0.0
NDefines.NCountry.RESISTANCE_DECAY_WHEN_NO_GROWTH = 100.0
NDefines.NResistance.INITIAL_STATE_RESISTANCE = 0.0
NDefines.NResistance.RESISTANCE_TARGET_BASE = 0.0
NDefines.NResistance.RESISTANCE_DECAY_BASE = 10.0
NDefines.NResistance.RESISTANCE_DECAY_MIN = 9.0
NDefines.NResistance.RESISTANCE_DECAY_MAX = 100.0
NDefines.NResistance.RESISTANCE_GROWTH_BASE = -10.0
NDefines.NResistance.RESISTANCE_GROWTH_MIN = -10.0
NDefines.NResistance.RESISTANCE_GROWTH_MAX = -100.0
NDefines.NResistance.COMPLIANCE_GROWTH_BASE = 20.0
NDefines.NResistance.COMPLIANCE_GROWTH_MIN = 0.0
NDefines.NResistance.COMPLIANCE_GROWTH_MAX = 100.0

	
NDefines.NResistance.INITIAL_STATE_RESISTANCE = 0
NDefines.NResistance.RESISTANCE_TARGET_MODIFIER_HAS_CLAIM = 0

NDefines.NResistance.RESISTANCE_TARGET_MODIFIER_PER_STABILITY_LOSS = 0
NDefines.NResistance.RESISTANCE_TARGET_MODIFIER_PER_COMPLIANCE = 0
	
NDefines.NResistance.RESISTANCE_TARGET_MODIFIER_IS_AT_PEACE = 0
	
NDefines.NResistance.RESISTANCE_TARGET_MODIFIER_STATE_VP = {					-- resistance target modifier pairs for vp. first entry is total vp in state and second entry is amount of target modifier that applies for that threshold
		0,   0.0, -- 0 - 5
		0,   0.0, -- 5 - 20
		0,  0.0, -- 20 - 50
		0,  0.0, -- 50 - ...
	}

NDefines.NResistance.RESISTANCE_TARGET_MODIFIER_OCCUPIED_CAPITULATED = 0.0
NDefines.NResistance.RESISTANCE_TARGET_MODIFIER_OCCUPIED_IS_EXILE_MIN = 0.0
NDefines.NResistance.RESISTANCE_TARGET_MODIFIER_OCCUPIED_IS_EXILE_MAX = 0.0

NDefines.NResistance.RESISTANCE_TARGET_MODIFIER_POP_LOW = 0.0
NDefines.NResistance.RESISTANCE_TARGET_MODIFIER_POP_VERY_LOW = 0.0
	







NDefines.NOperatives.BOOST_IDEOLOGY_NATIONAL_COVERAGE_FACTOR = 0;
NDefines.NOperatives.BOOST_IDEOLOGY_MAX_DRIFT_BY_OPERATIVE = 0;
NDefines.NOperatives.BOOST_IDEOLOGY_DRIFT_STACKING_FACTOR = 0;
NDefines.NOperatives.BOOST_IDEOLOGY_DAILY_XP_GAIN = 0;
NDefines.NOperatives.OPERATIVE_BASE_PROPAGANDA_POWER = 0;
NDefines.NOperatives.PROPAGANDA_OPERATIVE_STACKING_FACTOR = 0;
NDefines.NOperatives.PROPAGANDA_COUNTRY_STACKING_FACTOR = 0;
NDefines.NOperatives.PROPAGANDA_DAILY_XP_GAIN = 0;
NDefines.NOperatives.MIN_NATIONAL_COVERAGE_FOR_PROPAGANDA = 100;
NDefines.NOperatives.PROPAGANDA_SUB_NETWORK_STRENGTH_FACTOR = 0;
NDefines.NOperatives.OPERATIVE_BASE_CONTROL_TRADE_DRIFT = 0;
NDefines.NOperatives.CONTROL_TRADE_STACKING_FACTOR = 0;
NDefines.NOperatives.CONTROL_TRADE_MAX_INFLUENCE = 0;
NDefines.NOperatives.CONTROL_TRADE_INFLUENCE_DAILY_DECAY = 0;
NDefines.NOperatives.CONTROL_TRADE_DAILY_XP_GAIN = 0;
NDefines.NOperatives.OPERATIVE_BASE_DIPLOMATIC_PRESSURE_AI_ACCEPTANCE_SCORE_DRIFT = 0;
NDefines.NOperatives.DIPLOMATIC_PRESSURE_MAX_AI_ACCEPTANCE_SCORE_INCREASE = 0;
NDefines.NOperatives.DIPLOMATIC_PRESSURE_MAX_TENSION_REQUIREMENTS_DECREASE = 0;
NDefines.NOperatives.DIPLOMATIC_PRESSURE_DAILY_XP_GAIN = 0;
NDefines.NOperatives.AGENCY_CREATION_FACTORIES = 0
NDefines.NAI.MIN_DELIVERED_TRADE_FRACTION = 0.16	
NDefines.NAI.TRADEABLE_FACTORIES_FRACTION = 0.16
NDefines.NOperatives.AGENCY_CREATION_DAYS = 1
NDefines.NAI.DIPLOMACY_ACCEPT_ATTACHE_BASE = 100;
NDefines.NAI.DIPLOMACY_ACCEPT_ATTACHE_OPINION_TRASHHOLD = 0;
NDefines.NAI.DIPLOMACY_ACCEPT_ATTACHE_OPINION_PENALTY = 0;
NDefines.NAI.GIVE_STATE_CONTROL_MIN_CONTROLLED = 0;
NDefines.NAI.GIVE_STATE_CONTROL_MIN_CONTROL_DIFF = 0;
NDefines.NBuildings.INFRASTRUCTURE_RESOURCE_BONUS = 0.075;    --#0.2  было
NDefines.NAir.AIR_WING_MAX_SIZE = 2000
NDefines.NAir.AIR_DEPLOYMENT_DAYS = 0                              -- Down from 3

NDefines.NDiplomacy.NUM_DAYS_TO_ENABLE_KICKING_NEW_MEMBERS_OF_FACTION = 14	-- down from 90 | Number of days before being able to kick a new member of faction 
NDefines.NDiplomacy.NUM_DAYS_TO_ENABLE_REINVITE_KICKED_NATIONS = 14		-- down from 90 | Number of days before being able to re invite a kicked 


NDefines.NCharacter.SPECIALIST_ADVISOR_MIN_RANK = 2
NDefines.NCharacter.EXPERT_ADVISOR_MIN_RANK = 4
NDefines.NCharacter.GENIUS_ADVISOR_MIN_RANK = 6
NDefines.NCountry.BASE_MAX_COMMAND_POWER = 250.0

NDefines.NCountry.BASE_STABILITY_WAR_FACTOR = -0.15				-- Default stability war factor
NDefines.NCountry.BASE_STABILITY_PARTY_POPULARITY_FACTOR = 0.20	-- Default stability rulling party popularity factor
NDefines.NCountry.WAR_SUPPORT_OFFNSIVE_WAR = -0.1				-- Impact of being in offensive war
NDefines.NCountry.WAR_SUPPORT_DEFENSIVE_WAR = 0.2				-- Impact of being in defensive war
NDefines.NMilitary.CORPS_COMMANDER_DIVISIONS_CAP = 533			-- how many divisions a corps commander is limited to. 0 = inf < 0 = blocked
NDefines.NMilitary.FIELD_MARSHAL_DIVISIONS_CAP = 533			-- how many divisions a field marshall is limited to. 0 = inf < 0 = blocked
NDefines.NMilitary.GARRISON_ORDER_ARMY_CAP_FACTOR = 1.0			-- armies gets increased cap when they are garrisoned
NDefines.NMilitary.BASE_FORT_PENALTY = -0.2 
NDefines.NAir.AIR_WING_ATTACK_LOGISTICS_NO_TRUCK_DISRUPTION_FACTOR = 0.0 -- If a unit isn't motorized, still disrupt its supply by damage * this
NDefines.NAir.AIR_WING_ATTACK_LOGISTICS_TRUCK_DAMAGE_FACTOR = 0
NDefines.NAir.AIR_WING_ATTACK_LOGISTICS_TRAIN_DAMAGE_DISRUPTION_MITIGATION = 6.0 -- Multiply Train Damage by (Smooth / (Smooth + (Disruption * Mitigation)))
NDefines.NAir.AIR_WING_ATTACK_LOGISTICS_TRAIN_DAMAGE_DISRUPTION_SMOOTHING = 5.0

----- railway lost ---- -
NDefines.NAir.AIR_WING_ATTACK_LOGISTICS_RAILWAY_DAMAGE_SPILL_FACTOR	= 0
NDefines.NAir.AIR_WING_ATTACK_LOGISTICS_INFRA_DAMAGE_SPILL_FACTOR	= 0
NDefines.NAir.AIR_WING_ATTACK_LOGISTICS_TRAIN_DAMAGE_FACTOR = 0 
NDefines.NAir.AIR_WING_ATTACK_LOGISTICS_DISRUPTION_MIN_DAMAGE_FACTOR	= 0 
NDefines.NAir.AIR_WING_ATTACK_LOGISTICS_MAX_DISRUPTION_DAMAGE_TO_CONSIDER	= 0
NDefines.NAir.AIR_WING_ATTACK_LOGISTICS_DIRECT_DISRUPTION_DAMAGE_FACTOR	 =  0
NDefines.NAir.AIR_WING_ATTACK_LOGISTICS_TRUCK_MAX_FACTOR = 0 
------flit sooply - - -----

NDefines.NAir.MISSION_COMMAND_POWER_COSTS = {  -- command power cost per plane to create a mission
		0.0, -- AIR_SUPERIORITY
		0.0, -- CAS		
		0.0, -- INTERCEPTION	
		0.0, -- STRATEGIC_BOMBER
		0.0, -- NAVAL_BOMBER	
		0.0, -- DROP_NUKE		
		0.0, -- PARADROP		
		0.0, -- NAVAL_KAMIKAZE	
        0.0, -- PORT_STRIKE		
		0.0, -- AIR_SUPPLY		
		0.0, -- TRAINING
		0.0, -- NAVAL_MINES_PLANTING
		0.0, -- NAVAL_MINES_SWEEPING
	}
NDefines.NAir.COMBAT_DAMAGE_SCALE = 0.35 -- Vanilla = 1





NDefines.NMilitary.LAND_AIR_COMBAT_STR_DAMAGE_MODIFIER = 0.012   -- air global damage modifier
NDefines.NMilitary.LAND_AIR_COMBAT_ORG_DAMAGE_MODIFIER = 0.1    -- global damage modifier
NDefines.NMilitary.LAND_COMBAT_ORG_ARMOR_ON_SOFT_DICE_SIZE = 5

NDefines.NMilitary.LAND_AIR_COMBAT_MAX_PLANES_PER_ENEMY_WIDTH = 2 -- how many CAS/TAC can enter a combat depending on enemy width there

NDefines.NAir.ANTI_AIR_PLANE_DAMAGE_FACTOR = 0.8					-- Anti Air Gun Damage factor
NDefines.NAir.ANTI_AIR_PLANE_DAMAGE_CHANCE = 0.1					-- Anti Air Gun hit chance
NDefines.NAir.ANTI_AIR_MAXIMUM_DAMAGE_REDUCTION_FACTOR = 0.75	-- Maximum damage reduction factor applied to incoming air attacks against units with AA.
NDefines.NAir.ANTI_AIR_ATTACK_TO_DAMAGE_REDUCTION_FACTOR = 1.0	-- Balancing value to convert equipment stat anti_air_attack to the damage reduction modifier apply to incoming air attacks against units with AA.

-- Из CHADDFIXREBALANCE (Arthur): цены фокусов там урезаны вдвое (cost 10 -> 5), здесь так же для всех деревьев сразу.
NDefines.NFocus.FOCUS_POINT_DAYS = 3.5
