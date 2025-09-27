from __future__ import annotations
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple
from core.models import ParsedEntities, PowerRail, Oscillator, FunctionalTest


def parse_netlist(netlist_path: str) -> ParsedEntities:
    """Parse IPC-D-356A netlist format to extract hardware entities."""
    p = Path(netlist_path)
    if not p.exists():
        raise FileNotFoundError(f"Netlist file not found: {netlist_path}")
    
    content = p.read_text()
    lines = content.splitlines()
    
    # Extract project info
    title = "Unknown Board"
    for line in lines:
        if line.startswith("C  Project Name :"):
            title = line.split(":", 1)[1].strip()
            break
        elif line.startswith("C  Board Name :"):
            title = line.split(":", 1)[1].strip()
            break
    
    # Parse nets (lines starting with 327 or 317)
    nets = {}
    for line in lines:
        if line.startswith(("327", "317")):
            parts = line.split()
            if len(parts) >= 3:
                net_name = parts[1]  # Net name is the second field
                component_ref = parts[2]  # Component ref is the third field
                
                if net_name not in nets:
                    nets[net_name] = []
                nets[net_name].append(component_ref)
    
    # Extract power rails
    rails = []
    power_patterns = [
        r"(\d+)V",  # e.g., 3V3, 5V, 12V
        r"(\d+\.\d+)V",  # e.g., 1.8V, 2.5V
        r"VCC",  # VCC nets
        r"VDD",  # VDD nets
    ]
    
    for net_name, components in nets.items():
        # Skip GND nets
        if "GND" in net_name.upper():
            continue
            
        # Check if this looks like a power rail
        is_power = False
        voltage = None
        
        for pattern in power_patterns:
            match = re.search(pattern, net_name)
            if match:
                is_power = True
                try:
                    voltage = float(match.group(1))
                    break
                except ValueError:
                    pass
        
        # Also check for common power rail names
        if any(power_name in net_name.upper() for power_name in ["VCC", "VDD", "PWR", "POWER"]):
            is_power = True
            # Try to extract voltage from net name
            voltage_match = re.search(r"(\d+(?:\.\d+)?)", net_name)
            if voltage_match:
                voltage = float(voltage_match.group(1))
            else:
                voltage = 3.3  # Default assumption
        
        if is_power and voltage:
            rails.append(PowerRail(
                name=net_name,
                voltage=voltage,
                tolerance_mv=100  # Default tolerance
            ))
    
    # Extract oscillators (look for crystal components)
    oscillators = []
    crystal_components = set()
    
    for line in lines:
        if line.startswith(("327", "317")):
            parts = line.split()
            if len(parts) >= 2:
                component_ref = parts[1]
                # Look for crystal references (Y1, Y2, X1, X2, etc.)
                if re.match(r'^Y\d+$', component_ref) or re.match(r'^X\d+$', component_ref):
                    crystal_components.add(component_ref)
    
    # Add default oscillators for found crystals
    for i, crystal_ref in enumerate(sorted(crystal_components), 1):
        # Default frequencies - could be enhanced with BOM lookup
        default_freqs = [16000000, 32000000, 8000000, 12000000]  # Common crystal frequencies
        freq = default_freqs[i % len(default_freqs)]
        
        oscillators.append(Oscillator(
            ref=crystal_ref,
            frequency_hz=freq,
            tolerance_hz=100000  # Default tolerance
        ))
    
    # Extract functional tests (look for test points and connectors)
    functional_tests = []
    test_points = set()
    connectors = set()
    
    for line in lines:
        if line.startswith(("327", "317")):
            parts = line.split()
            if len(parts) >= 2:
                component_ref = parts[1]
                # Look for test points
                if component_ref.startswith("TP"):
                    test_points.add(component_ref)
                # Look for connectors
                elif component_ref.startswith("J") or component_ref.startswith("P"):
                    connectors.add(component_ref)
    
    # Add functional tests based on found components
    if test_points:
        functional_tests.append(FunctionalTest(
            name="Test Point Verification",
            command="check_test_points",
            expected="All test points accessible"
        ))
    
    if connectors:
        functional_tests.append(FunctionalTest(
            name="Connector Interface Test",
            command="test_connectors",
            expected="All connectors functional"
        ))
    
    # Add default functional tests
    functional_tests.extend([
        FunctionalTest(
            name="Power-On Self Test",
            command="post",
            expected="PASS"
        ),
        FunctionalTest(
            name="Communication Test",
            command="comm_test",
            expected="All interfaces responsive"
        )
    ])
    
    return ParsedEntities(
        title=title,
        rails=rails,
        oscillators=oscillators,
        functional_tests=functional_tests
    )


def extract_test_points(netlist_path: str) -> List[Dict]:
    """Extract test point information from netlist."""
    p = Path(netlist_path)
    if not p.exists():
        return []
    
    content = p.read_text()
    lines = content.splitlines()
    
    test_points = []
    for line in lines:
        if line.startswith(("327", "317")):
            parts = line.split()
            if len(parts) >= 2:
                component_ref = parts[1]
                if component_ref.startswith("TP"):
                    # Extract coordinates if available
                    coords = {}
                    for part in parts:
                        if "X" in part and "Y" in part:
                            try:
                                x_match = re.search(r'X(\d+)', part)
                                y_match = re.search(r'Y(\d+)', part)
                                if x_match and y_match:
                                    coords = {
                                        "x": int(x_match.group(1)),
                                        "y": int(y_match.group(1))
                                    }
                                    break
                            except (ValueError, AttributeError):
                                pass
                    
                    test_points.append({
                        "ref": component_ref,
                        "net": parts[0],
                        "coordinates": coords
                    })
    
    return test_points
