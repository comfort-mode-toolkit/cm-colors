from cm_colors import make_readable_bulk

print('--- Testing Bulk API ---')

pairs = [
    ('#000000', '#ffffff'),  # Already readable (AAA)
    ('#ffffff', '#ffffff'),  # Unreadable
    ('#777777', '#ffffff'),  # Grey (needs fix)
    ('#777777', '#ffffff', True),  # Grey large text (needs less fix)
    ((119, 119, 119), (255, 255, 255)),  # Tuple input (Grey on White)
]

print(f'Input pairs: {pairs}')

results = make_readable_bulk(pairs, save_report=True)

print('\nResults:')
for i, (color, status) in enumerate(results):
    print(f'  Pair {i+1}: {color} - {status}')

print('\n--- Verification Complete ---')
