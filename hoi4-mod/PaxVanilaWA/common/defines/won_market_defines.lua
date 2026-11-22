-- Wealth of Nations - International Market module (merged from Arsenal of Nations)
-- Arsenal of Nations: the AI takes part in the International Market more often.
-- Only AI market keys are changed; every other define keeps its vanilla value.

NDefines.NAI.EQUIPMENT_MARKET_UPDATE_FREQUENCY_DAYS = 7            -- vanilla 11: the AI checks the market more often
NDefines.NAI.EQUIPMENT_MARKET_MAX_CIVS_FOR_PURCHASES_RATIO = 0.15   -- vanilla 0.1: the AI may spend more factories on purchases
NDefines.NAI.EQUIPMENT_MARKET_BASE_MARKET_RATIO = 0.3               -- vanilla 0.2: the AI lists more of its surplus for sale
NDefines.NAI.EQUIPMENT_MARKET_SCORE_FACTOR_DIPLO_OPINION = 2.0      -- vanilla 1.0: good relations (exhibitions, trade) matter more to buyers
NDefines.NAI.EQUIPMENT_MARKET_SCORE_FACTOR_COST_PER_UNIT = -3.0          -- vanilla -5.0: price matters a little less than the seller
NDefines.NAI.EQUIPMENT_MARKET_NR_DELIVERIES_SOFT_MAX = 14               -- vanilla 10: the AI accepts larger, longer contracts
NDefines.NAI.EQUIPMENT_MARKET_SHORTAGE_DAYS_TO_CANCEL = 60              -- vanilla 30: the AI is slower to cancel contracts that deliver slowly
