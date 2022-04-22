
from credmark.cmf.model import Model
from credmark.cmf.model.errors import ModelRunError
from credmark.cmf.types import Address, NativeToken, Token
from credmark.dto import DTO, DTOField
from models.dtos.example import ExampleModelOutput


class _TokenLoadingInput(DTO):
    address: Address = DTOField(default='0x68cfb82eacb9f198d508b514d898a403c449533e')
    symbol: str = DTOField(default='AAVE')


@Model.describe(slug='example.token-loading',
                version='1.0',
                developer='credmark',
                input=_TokenLoadingInput,
                output=ExampleModelOutput)
class ExampleTokenLoading(Model):
    """
        This model demonstrates the functionality of the Token class
    """

    def run(self, input: _TokenLoadingInput) -> ExampleModelOutput:
        output = ExampleModelOutput(
            github_url="https://github.com/credmark/credmark-models-py/blob/main/models/examples/06_token_examples.py",
            documentation_url="https://developer-docs.credmark.com/en/latest/reference/credmark.cmf.types.token.html")

        output.log("Token class is an ERC20 contract")

        output.log("Token can be initialized from address")
        tokenLoadedFromAddress = Token(address=input.address)
        output.log_io(input=f"Token(address='{input.address}')", output={tokenLoadedFromAddress})

        output.log("Token can also be initialized from symbol")
        tokenLoadedFromSymbol = Token(symbol=input.symbol)
        output.log_io(input=f"Token(symbol='{input.symbol}')", output=tokenLoadedFromSymbol)

        output.log("Token's meta info has its symbol, name, decimals "
                   "and total supply along with contract metadata")
        output.log_io(input="tokenLoadedFromAddress.name",
                      output=tokenLoadedFromAddress.name)
        output.log_io(input="tokenLoadedFromAddress.symbol",
                      output=tokenLoadedFromAddress.symbol)
        output.log_io(input="tokenLoadedFromAddress.decimals",
                      output=tokenLoadedFromAddress.decimals)
        output.log_io(input="tokenLoadedFromAddress.total_supply",
                      output=tokenLoadedFromAddress.total_supply)

        output.log("Token amount can be converted from base unit to scaled unit using scaled utility method")
        output.log_io(input="tokenLoadedFromAddress.scaled(tokenLoadedFromAddress.total_supply)",
                      output=f"{tokenLoadedFromAddress.scaled(tokenLoadedFromAddress.total_supply)}")

        output.log("Ethereum token can be obtained using NativeToken")
        output.log_io(input="NativeToken()", output=NativeToken())

        try:
            Token(address="0xInvalidAddress00000")
            raise ModelRunError(
                message="Token cannot be initialized with an invalid address, "
                "an exception was NOT caught, and the example has FAILED")
        except ValueError as _e:
            output.log_error(_e)
            output.log_error(
                "Attempting to initialize a Token with invalid address "
                "raises ValueError")

        # try:
        #     Token(symbol="INVSYM")
        #     raise ModelRunError(
        #         message="Token cannot be initialized with an invalid symbol, an exception was NOT caught, "
        #         "and the example has FAILED")
        # except ModelDataError as _e:
        #     output.log(_e)
        #     output.log(
        #         "Attempting to initialize a Token with invalid symbol "
        #         "raises ModelDataError")

        return output
