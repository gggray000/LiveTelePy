
# TODO: Verify the usage
def decode_can_message(dbc, arbitration_id, can_data):
    try:
        msg = dbc.get_message_by_frame_id(arbitration_id)
        decoded = msg.decode(can_data)
        return msg.name, decoded
    except Exception as e:
        print(f"[CAN] Failed to decode ID {arbitration_id}: {e}")
        return None, {}
