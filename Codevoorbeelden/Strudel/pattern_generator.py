#!/usr/bin/env python3
"""
Strudel Pattern Generator for MQTT
Generates MQTT patterns from sound patterns with optional color mapping
"""

import re
import sys


def generate_mqtt_pattern(sound_pattern, trigger_sounds=None, color_map=None):
    """
    Generate MQTT pattern from sound pattern.

    Args:
        sound_pattern: String like "bd bd hh bd rim bd hh bd, - - - - jazz - - -"
        trigger_sounds: List of sounds that should trigger MQTT (default: ['bd'])
        color_map: Dict mapping sounds to colors (e.g., {'bd': 'purple', 'rim': 'green'})

    Returns:
        tuple: (control_pattern, color_pattern) for MQTT
    """
    if trigger_sounds is None:
        trigger_sounds = ['bd']

    # Split pattern into tokens (words and separators)
    tokens = re.findall(r'\w+|[^\w\s]|\s+', sound_pattern)

    control_tokens = []
    color_tokens = []

    for token in tokens:
        # Keep whitespace and special characters as-is
        if not re.match(r'\w+', token):
            control_tokens.append(token)
            color_tokens.append(token)
        # Replace trigger sounds with 'on' for control
        elif token in trigger_sounds:
            control_tokens.append('on')
            # Add color if mapping exists
            if color_map and token in color_map:
                color_tokens.append(color_map[token])
            else:
                color_tokens.append('on')
        # Replace everything else with '-'
        else:
            control_tokens.append('-')
            color_tokens.append('-')

    control_pattern = ''.join(control_tokens)
    color_pattern = ''.join(color_tokens)

    return control_pattern, color_pattern


def generate_strudel_code(sound_pattern, trigger_sounds=None, color_map=None,
                          broker='mqtt.rubu.be', port=9003, use_colors=False):
    """
    Generate complete Strudel code with MQTT patterns.

    Args:
        sound_pattern: The sound pattern string
        trigger_sounds: List of sounds to trigger MQTT
        color_map: Dict mapping sounds to colors
        broker: MQTT broker address
        port: MQTT broker WebSocket port
        use_colors: Whether to include color changes
    """
    control_pattern, color_pattern = generate_mqtt_pattern(sound_pattern, trigger_sounds, color_map)

    code = f'''// MQTT synchroon met instrumenten
const soundPattern = "{sound_pattern}"
const controlPattern = "{control_pattern}"  // Triggers LED flash
'''

    if use_colors and color_map:
        code += f'''const colorPattern = "{color_pattern}"  // Color changes

stack(
  sound(soundPattern).scope(),
  sound(controlPattern).mqtt('strudel', 'qifj3258', 'strudel/control', 'wss://{broker}:{port}/mqtt', 'strudelid437354', 0),
  sound(colorPattern).mqtt('strudel', 'qifj3258', 'strudel/color', 'wss://{broker}:{port}/mqtt', 'strudelid437354', 0)
)
'''
    else:
        code += f'''
stack(
  sound(soundPattern).scope(),
  sound(controlPattern).mqtt('strudel', 'qifj3258', 'strudel/control', 'wss://{broker}:{port}/mqtt', 'strudelid437354', 0)
)
'''

    return code


def main():
    """Main function with example usage."""
    print("=" * 60)
    print("Strudel MQTT Pattern Generator")
    print("=" * 60)
    print()

    # Example pattern
    sound_pattern = "bd bd hh bd rim bd hh bd, - - - - jazz - - -"

    # Example 1: Simple - flash on all 'bd'
    print("Example 1: Flash on bass drum (bd)")
    print("-" * 60)
    control_pattern, _ = generate_mqtt_pattern(sound_pattern, trigger_sounds=['bd'])
    print(f"Sound:   {sound_pattern}")
    print(f"Control: {control_pattern}")
    print()

    # Example 2: Flash on bd and rim
    print("Example 2: Flash on bass drum (bd) and rim")
    print("-" * 60)
    control_pattern, _ = generate_mqtt_pattern(sound_pattern, trigger_sounds=['bd', 'rim'])
    print(f"Sound:   {sound_pattern}")
    print(f"Control: {control_pattern}")
    print()

    # Example 3: With colors
    print("Example 3: Purple on bd, Green on rim")
    print("-" * 60)
    color_map = {'bd': 'magenta', 'rim': 'green'}  # magenta = purple
    control_pattern, color_pattern = generate_mqtt_pattern(
        sound_pattern,
        trigger_sounds=['bd', 'rim'],
        color_map=color_map
    )
    print(f"Sound:   {sound_pattern}")
    print(f"Control: {control_pattern}")
    print(f"Color:   {color_pattern}")
    print()

    # Example 4: Complete Strudel code
    print("Example 4: Complete Strudel code with colors")
    print("-" * 60)
    code = generate_strudel_code(
        sound_pattern,
        trigger_sounds=['bd', 'rim'],
        color_map={'bd': 'magenta', 'rim': 'green'},
        use_colors=True
    )
    print(code)

    # Interactive mode
    print()
    print("=" * 60)
    print("Interactive Mode")
    print("=" * 60)

    # Get user input
    user_pattern = input("\nEnter your sound pattern (or press Enter for default): ").strip()
    if not user_pattern:
        user_pattern = sound_pattern

    # Ask about colors
    use_colors = input("Use colors? (y/n, default=n): ").strip().lower() == 'y'

    if use_colors:
        print("\nAvailable colors: red, green, blue, white, cyan, magenta, yellow, random")
        bd_color = input("Color for 'bd' (default=magenta): ").strip() or 'magenta'
        rim_color = input("Color for 'rim' (default=green): ").strip() or 'green'
        color_map = {'bd': bd_color, 'rim': rim_color}
        trigger_sounds = ['bd', 'rim']
    else:
        color_map = None
        trigger_sounds = ['bd']

    # Generate code
    print("\n" + "=" * 60)
    print("Generated Strudel Code:")
    print("=" * 60)
    code = generate_strudel_code(user_pattern, trigger_sounds, color_map, use_colors=use_colors)
    print(code)

    # Save option
    save = input("\nSave to file? (y/n): ").strip().lower()
    if save == 'y':
        filename = input("Filename (default=generated_pattern.txt): ").strip() or "generated_pattern.txt"
        with open(filename, 'w') as f:
            f.write(code)
        print(f"Saved to {filename}")


if __name__ == "__main__":
    main()
