# pylint:disable=line-too-long

from credmark.cmf.model import Model
from credmark.cmf.types import Portfolio, Position, Some
from credmark.dto import EmptyInput
from models.credmark.algorithms.value_at_risk.dto import (ContractVaRInput,
                                                          PortfolioVaRInput,
                                                          VaRHistoricalOutput)
from models.credmark.protocols.lending.aave.aave_v2 import AaveDebtInfo


@Model.describe(slug="finance.var-aave",
                version="1.2",
                display_name="Aave V2 VaR",
                description="Calculate the VaR of Aave contract of its net asset",
                category='protocol',
                subcategory='aave-v2',
                tags=['var'],
                input=ContractVaRInput,
                output=VaRHistoricalOutput)
class AaveV2GetVAR(Model):
    """
    VaR of Aave based on its inventory of tokens.
    The exposure of Aave is the number of tokens borrowed (totalDebt)
    less than the total numbe of tokens (totalSupply) deposited.

    - totalSupply of aToken is Aave's liability / loaner's asset, hence a negative sign
    - totalDebt is Aava's asset / borrower's liability, hence a positive sign
    - exposure = dbt.totalDebt_qty - dbt.totalSupply_qty = -dbt.totalLiquidity = (totalSupply - totalDebt)

    Reference:
    https://docs.credmark.com/risk-insights/research/aave-and-compound-historical-var
    """

    def run(self, input: ContractVaRInput) -> VaRHistoricalOutput:
        debts = self.context.run_model('aave-v2.lending-pool-assets',
                                       input=EmptyInput(),
                                       return_type=Some[AaveDebtInfo])

        n_debts = len(debts.some)
        positions = []
        for n_dbt, dbt in enumerate(debts):
            self.logger.debug(f'{n_dbt+1}/{n_debts} {dbt.aToken.address=} '
                              f'{dbt.totalLiquidity_qty=} '
                              f'from {dbt.totalSupply_qty=}-{dbt.totalDebt_qty=}')
            # Note below is taking the negated totalLiquidity as -totalSupply_qty + totalDebt_qty
            # See the doc of this class
            positions.append(Position(amount=-dbt.totalLiquidity_qty, asset=dbt.token))
        portfolio = Portfolio(positions=positions)

        var_input = PortfolioVaRInput(portfolio=portfolio, **input.dict())
        return self.context.run_model(slug='finance.var-portfolio-historical',
                                      input=var_input,
                                      return_type=VaRHistoricalOutput)
