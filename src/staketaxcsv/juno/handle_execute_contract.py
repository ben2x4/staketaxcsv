from staketaxcsv.common.ExporterTypes import TX_TYPE_UNKNOWN, TX_TYPE_TRADE
import staketaxcsv.common.ibc.handle
import staketaxcsv.common.ibc.make_tx
import staketaxcsv.common.ibc.util_ibc


def handle_execute_contract(exporter, txinfo, msginfo):
    transfers_in, transfers_out = msginfo.transfers
    transfers_in.extend(get_cw20_transfers_in(msginfo))
    transfers_out.extend(get_cw20_transfers_out(msginfo))

    rows = []
    if len(transfers_in) == 0 and len(transfers_out) == 0:
        rows.append(staketaxcsv.common.ibc.make_tx._make_tx(txinfo, msginfo, "", "", "", "", tx_type=TX_TYPE_UNKNOWN))
    elif len(transfers_in) == 1 and len(transfers_out) == 1:
        sent_amount, sent_currency = transfers_out[0]
        received_amount, received_currency = transfers_in[0]
        rows.append(staketaxcsv.common.ibc.make_tx._make_tx(txinfo, msginfo, sent_amount, sent_currency, received_amount, received_currency, tx_type=TX_TYPE_TRADE))
    else:
        # Handle unknown transaction as separate transfers for each row.
        for sent_amount, sent_currency in transfers_out:
            rows.append(
                staketaxcsv.common.ibc.make_tx._make_tx(txinfo, msginfo, sent_amount, sent_currency, "", "", tx_type=TX_TYPE_UNKNOWN))
        for received_amount, received_currency in transfers_in:
            rows.append(
                staketaxcsv.common.ibc.make_tx._make_tx(txinfo, msginfo, "", "", received_amount, received_currency, tx_type=TX_TYPE_UNKNOWN))

    staketaxcsv.common.ibc.util_ibc._ingest_rows(exporter, txinfo, msginfo, rows, "")


def get_cw20_transfers_in(msginfo):
    transfers = []
    for msg in msginfo.wasm:
        if is_cw20_transfer_message(msg) and msg.get("to") == msginfo.message.get("sender"):
            transfers.append((msg.get("amount"), msg.get("_contract_address")))
    return transfers


def get_cw20_transfers_out(msginfo):
    transfers = []
    for msg in msginfo.wasm:
        if (is_cw20_transfer_message(msg) or is_cw20_transfer_from_message(msg)) and msg.get("from") == msginfo.message.get("sender"):
            transfers.append((msg.get("amount"), msg.get("_contract_address")))
    return transfers


def is_cw20_transfer_message(msg):
    return msg.get("action") == "transfer" and msg.get("from") and msg.get("to") and msg.get("amount")


def is_cw20_transfer_from_message(msg):
    return msg.get("action") == "transfer_from" and msg.get("from") and msg.get("to") and msg.get("amount") and msg.get("by")
