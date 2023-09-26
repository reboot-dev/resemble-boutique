import uuid
from datetime import timedelta
from microservices_demo.api import demo_pb2
from microservices_demo.api.demo_rsm import Shipping
from resemble.aio.contexts import ReaderContext, WriterContext


class ShippingServicer(Shipping.Interface):

    async def GetQuote(
        self,
        context: WriterContext,
        state: demo_pb2.ShippingState,
        request: demo_pb2.GetQuoteRequest,
    ) -> Shipping.GetQuoteEffects:
        quote = demo_pb2.ShippingQuote(
            id=str(uuid.uuid4()),
            cost=demo_pb2.Money(
                currency_code="USD",
                units=8,
                nanos=(99 * 10000000),
            ),
        )

        state.quotes.append(quote)

        expire_quote_task = self.schedule(
            timedelta(seconds=request.quote_expiration_seconds),
        ).ExpireQuoteTask(
            context,
            quote=quote,
        )

        return Shipping.GetQuoteEffects(
            state=state,
            response=demo_pb2.GetQuoteResponse(quote=quote),
            tasks=[expire_quote_task],
        )

    async def PrepareShipOrder(
        self,
        context: WriterContext,
        state: demo_pb2.ShippingState,
        request: demo_pb2.PrepareShipOrderRequest,
    ) -> Shipping.PrepareShipOrderEffects:
        # Remove the quote, unless it is missing implying it has been
        # expired, in which case we raise an error.
        valid_quote = False
        i = 0
        while i < len(state.quotes):
            if state.quotes[i].id == request.quote.id:
                valid_quote = True
                del state.quotes[i]
                break
            i += 1

        if not valid_quote:
            raise Shipping.PrepareShipOrderError(
                demo_pb2.ShippingQuoteInvalidOrExpired()
            )

        # Create a task to actually do the shipping since that is not
        # compensatable and if we are called from within a transaction
        # we only want to actually do the shipping if the transaction
        # commits (and thus our task gets dispatched).
        ship_order_task = self.schedule().ShipOrderTask(context)

        return Shipping.PrepareShipOrderEffects(
            state=state,
            response=demo_pb2.PrepareShipOrderResponse(
                tracking_id=str(uuid.uuid4()),
            ),
            tasks=[ship_order_task],
        )

    async def ExpireQuoteTask(
        self,
        context: WriterContext,
        state: demo_pb2.ShippingState,
        request: demo_pb2.ExpireQuoteTaskRequest,
    ) -> Shipping.ExpireQuoteTaskEffects:
        # Remove the quote.
        quotes = [
            quote for quote in state.quotes if quote.id != request.quote.id
        ]
        del state.quotes[:]
        state.quotes.extend(quotes)

        return Shipping.ExpireQuoteTaskEffects(
            state=state,
            response=demo_pb2.Empty(),
        )

    async def ShipOrderTask(
        self,
        context: ReaderContext,
        state: demo_pb2.ShippingState,
        request: demo_pb2.ShipOrderTaskRequest,
    ) -> demo_pb2.Empty:
        # This is where we'd actually do the shipping, retrying if we
        # get an error.
        return demo_pb2.Empty()
