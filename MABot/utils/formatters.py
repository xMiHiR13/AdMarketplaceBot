async def get_readable_time(seconds: int) -> str:
    # Calculate years, months, weeks, days, hours, minutes, and remaining seconds
    years, seconds = divmod(seconds, 365 * 24 * 3600)
    months, seconds = divmod(seconds, 30 * 24 * 3600)
    weeks, seconds = divmod(seconds, 7 * 24 * 3600)
    days, seconds = divmod(seconds, 24 * 3600)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    # Build the formatted string
    readable_time = ""
    if years > 0:
        readable_time += f"{years}ʏᴇᴀʀ{'s' if years > 1 else ''}, "
    if months > 0:
        readable_time += f"{months}ᴍᴏɴᴛʜ{'s' if months > 1 else ''}, "
    if weeks > 0:
        readable_time += f"{weeks}ᴡᴇᴇᴋ, "
    if days > 0:
        readable_time += f"{days}ᴅᴀʏ{'s' if days > 1 else ''}, "
    readable_time += f"{hours}ʜ:{minutes}ᴍ:{seconds}s"

    return readable_time
