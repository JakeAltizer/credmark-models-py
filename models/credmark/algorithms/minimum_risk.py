from credmark.cmf.model import Model
from credmark.cmf.types import Some, Tokens
from credmark.dto import DTO, EmptyInput
from models.credmark.protocols.lending.aave.aave_v2 import AaveDebtInfo
from models.credmark.protocols.lending.compound.compound_v2 import \
    CompoundV2PoolInfo


class MinRiskOutput(DTO):
    min_risk_rate: float


@Model.describe(slug="finance.min-risk-rate",
                version="1.1",
                display_name="Calculate minimal risk rate",
                description='Rates from stablecoins\' loans to Aave and Compound, '
                            'then weighted by their debt size and total supply',
                category='financial',
                input=EmptyInput,
                output=MinRiskOutput)
class MinRisk(Model):
    """
    Doc is
        https://docs.credmark.com/smart-money-in-defi/investment-concepts/minimum-risk-rate-of-defi
    """

    def run(self, _) -> MinRiskOutput:
        aave_debts = self.context.run_model('aave-v2.lending-pool-assets',
                                            input=EmptyInput(),
                                            return_type=Some[AaveDebtInfo])

        stable_coins = Tokens(**self.context.models.token.stablecoins())
        sb_debt_infos = {}
        sb_tokens = {}
        for dbt in aave_debts:
            token = dbt.token
            if token in stable_coins:
                dbt_info = sb_debt_infos.get(token.address, [])
                rate = dbt.supplyRate
                supply_qty = dbt.totalSupply_qty
                sb_debt_infos[token.address] = dbt_info + [(rate, supply_qty)]
                sb_tokens[token.address] = dbt.token

        compound_debts = self.context.run_model('compound-v2.all-pools-info',
                                                input=EmptyInput(),
                                                return_type=Some[CompoundV2PoolInfo])

        for dbt in compound_debts:
            token = dbt.token
            if token in stable_coins:
                dbt_info = sb_debt_infos.get(token.address, [])
                rate = dbt.supplyAPY
                supply_qty = dbt.totalLiability
                sb_debt_infos[token.address] = dbt_info + [(rate, supply_qty)]

        weighted_supply = 0
        all_sb_supply = 0
        for sb_address, info in sb_debt_infos.items():
            weighted_rate = sum(r * q for r, q in info) / sum(q for _r, q in info)
            scaled_supply = sb_tokens[sb_address].scaled(sb_tokens[sb_address].total_supply)
            weighted_supply += weighted_rate * scaled_supply
            all_sb_supply += scaled_supply

        supply_weighted_rate = weighted_supply / all_sb_supply
        return MinRiskOutput(min_risk_rate=supply_weighted_rate)
