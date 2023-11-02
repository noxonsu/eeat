

import uti

# Filter out entries with "nature" set to "invalid"
filtered_data = {key: value for key, value in data.items() if value.get("nature") != "invalid"}

# Print the filtered data
print(filtered_data)