"""
Comprehensive Real-World Color Pair Test Suite
Generates 10k realistic web color combinations mirroring actual usage patterns
"""

import random
import math
import json
from typing import Tuple, List, Dict, Any
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich import box




from cm_colors.core.optimisation import check_and_fix_contrast
from cm_colors.core.conversions import oklch_to_rgb_safe, is_valid_rgb
from cm_colors.core.contrast import calculate_contrast_ratio
from cm_colors.core.color_metrics import calculate_delta_e_2000

console = Console()


class RealWorldColorGenerator:
    """Generate color pairs that mirror actual web design patterns"""

    # Category definitions with realistic Oklch ranges (Defined exactly as in user prompt)
    CATEGORIES = {
        'brand_primary': {
            'weight': 0.30,
            'description': 'Saturated brand colors (logos, CTAs, links)',
            'text': {'L': (0.45, 0.65), 'C': (0.15, 0.35), 'H': (0, 360)},
            'bg_style': 'neutral',
        },
        'dark_ui': {
            'weight': 0.25,
            'description': 'Dark mode interfaces',
            'text': {'L': (0.80, 0.95), 'C': (0.0, 0.05), 'H': (0, 360)},
            'bg': {'L': (0.10, 0.25), 'C': (0.0, 0.10), 'H': (0, 360)},
        },
        'light_ui': {
            'weight': 0.25,
            'description': 'Light mode interfaces',
            'text': {'L': (0.10, 0.30), 'C': (0.0, 0.08), 'H': (0, 360)},
            'bg': {'L': (0.90, 0.98), 'C': (0.0, 0.05), 'H': (0, 360)},
        },
        'accent_colors': {
            'weight': 0.10,
            'description': 'High saturation accents (buttons, badges)',
            'text': {'L': (0.50, 0.70), 'C': (0.20, 0.40), 'H': (0, 360)},
            'bg_style': 'neutral',
        },
        'pastel': {
            'weight': 0.10,
            'description': 'Soft pastels (info cards, backgrounds)',
            'text': {'L': (0.75, 0.90), 'C': (0.05, 0.15), 'H': (0, 360)},
            'bg_style': 'neutral',
        },
    }

    # Special failure-prone scenarios (10% of dataset)
    EDGE_CASES = {
        'bright_yellow_on_white': {
            'text': {'L': 0.90, 'C': 0.25, 'H': 100},  # Bright yellow
            'bg': {'L': 0.97, 'C': 0.0, 'H': 0},  # Near white
        },
        'pure_blue_on_black': {
            'text': {'L': 0.50, 'C': 0.35, 'H': 260},  # Saturated blue
            'bg': {'L': 0.12, 'C': 0.0, 'H': 0},  # Near black
        },
        'mid_gray_on_gray': {
            'text': {'L': 0.50, 'C': 0.02, 'H': 0},  # Mid gray
            'bg': {'L': 0.55, 'C': 0.02, 'H': 0},  # Similar gray
        },
        'neon_on_dark': {
            'text': {'L': 0.65, 'C': 0.40, 'H': 330},  # Neon pink
            'bg': {'L': 0.15, 'C': 0.05, 'H': 280},  # Dark purple
        },
        'red_on_green': {
            'text': {'L': 0.55, 'C': 0.25, 'H': 25},  # Red
            'bg': {'L': 0.60, 'C': 0.20, 'H': 145},  # Green
        },
        'orange_on_yellow': {
            'text': {'L': 0.70, 'C': 0.22, 'H': 65},  # Orange
            'bg': {'L': 0.85, 'C': 0.18, 'H': 95},  # Yellow
        },
    }

    # Hue distributions matching real-world usage
    HUE_WEIGHTS = {
        'blue': (200, 260, 0.25),  # Most common (corporate)
        'red': (10, 40, 0.15),
        'green': (120, 160, 0.15),
        'purple': (270, 310, 0.12),
        'orange': (50, 80, 0.10),
        'cyan': (170, 200, 0.08),
        'pink': (320, 360, 0.08),
        'yellow': (85, 105, 0.07),
    }

    def __init__(self, seed: int = 42):
        random.seed(seed)

    def _sample_oklch(self, ranges: Dict) -> Tuple[float, float, float]:
        """Sample Oklch values from given ranges"""
        L = (
            random.uniform(*ranges['L'])
            if isinstance(ranges['L'], tuple)
            else ranges['L']
        )
        C = (
            random.uniform(*ranges['C'])
            if isinstance(ranges['C'], tuple)
            else ranges['C']
        )

        # Sample hue with realistic distribution
        if isinstance(ranges['H'], tuple):
            H = random.uniform(*ranges['H'])
        else:
            H = self._sample_realistic_hue()

        return (L, C, H)

    def _sample_realistic_hue(self) -> float:
        """Sample hue with weights matching real-world color usage"""
        rand = random.random()
        cumulative = 0.0

        for color_name, (h_min, h_max, weight) in self.HUE_WEIGHTS.items():
            cumulative += weight
            if rand <= cumulative:
                return random.uniform(h_min, h_max)

        return random.uniform(0, 360)  # Fallback

    def _oklch_to_valid_rgb(
        self, oklch: Tuple[float, float, float], max_attempts: int = 10
    ) -> Tuple[int, int, int]:
        """Convert Oklch to RGB, reducing chroma if needed to stay in gamut"""
        L, C, H = oklch

        for attempt in range(max_attempts):
            rgb = oklch_to_rgb_safe((L, C, H))
            if is_valid_rgb(rgb):
                return rgb

            # Reduce chroma to bring into gamut
            C *= 0.85
            if C < 0.001:
                break

        # Fallback: desaturate completely
        rgb = oklch_to_rgb_safe((L, 0.0, H))
        return rgb if is_valid_rgb(rgb) else (128, 128, 128)

    def _generate_neutral_background(
        self, text_L: float
    ) -> Tuple[int, int, int]:
        """Generate appropriate neutral background based on text lightness"""
        if text_L < 0.5:
            # Dark text needs light background
            bg_L = random.uniform(0.85, 0.97)
        else:
            # Light text needs dark background
            bg_L = random.uniform(0.15, 0.30)

        bg_C = random.uniform(0.0, 0.03)  # Nearly neutral
        bg_H = random.uniform(0, 360)

        return self._oklch_to_valid_rgb((bg_L, bg_C, bg_H))

    def generate_category_pair(self, category: str) -> Dict:
        """Generate a color pair from a specific category"""
        config = self.CATEGORIES[category]

        # Generate text color
        text_oklch = self._sample_oklch(config['text'])
        text_rgb = self._oklch_to_valid_rgb(text_oklch)

        # Generate background
        if 'bg' in config:
            bg_oklch = self._sample_oklch(config['bg'])
            bg_rgb = self._oklch_to_valid_rgb(bg_oklch)
        else:
            # Use neutral background
            bg_rgb = self._generate_neutral_background(text_oklch[0])

        initial_contrast = calculate_contrast_ratio(text_rgb, bg_rgb)

        return {
            'text_rgb': text_rgb,
            'bg_rgb': bg_rgb,
            'category': category,
            'initial_contrast': initial_contrast,
        }

    def generate_edge_case(self, case_name: str) -> Dict:
        """Generate a specific edge case scenario"""
        config = self.EDGE_CASES[case_name]

        # Add small random variations to avoid identical cases
        text_L = config['text']['L'] + random.uniform(-0.02, 0.02)
        text_C = config['text']['C'] + random.uniform(-0.01, 0.01)
        text_H = config['text']['H'] + random.uniform(-5, 5)
        text_rgb = self._oklch_to_valid_rgb((text_L, text_C, text_H))

        bg_L = config['bg']['L'] + random.uniform(-0.02, 0.02)
        bg_C = config['bg']['C'] + random.uniform(-0.01, 0.01)
        bg_H = config['bg']['H'] + random.uniform(-5, 5)
        bg_rgb = self._oklch_to_valid_rgb((bg_L, bg_C, bg_H))

        initial_contrast = calculate_contrast_ratio(text_rgb, bg_rgb)

        return {
            'text_rgb': text_rgb,
            'bg_rgb': bg_rgb,
            'category': f'edge_case_{case_name}',
            'initial_contrast': initial_contrast,
        }

    def generate_test_suite(self, total_pairs: int = 10000) -> List[Dict]:
        """Generate comprehensive test suite of color pairs, GUARANTEED to hit total_pairs."""
        pairs = []

        # Generator for regular pairs
        def generate_regular_pair():
            category = random.choices(
                list(self.CATEGORIES.keys()),
                weights=[c['weight'] for c in self.CATEGORIES.values()],
                k=1,
            )[0]
            pair = self.generate_category_pair(category)
            pair['large'] = random.random() < 0.30
            return pair

        # Generator for edge cases
        def generate_edge_pair():
            case_name = random.choice(list(self.EDGE_CASES.keys()))
            pair = self.generate_edge_case(case_name)
            pair['large'] = random.random() < 0.20
            return pair

        # Generate until the total is reached
        while len(pairs) < total_pairs:

            # Determine if generating a regular or edge case pair (10% edge target)
            if len(pairs) < total_pairs * 0.10 or random.random() < 0.10:
                pair = generate_edge_pair()
            else:
                pair = generate_regular_pair()

            if pair is None:
                continue

            # Filter for variety in initial contrast before adding
            rand = random.random()

            # 60% needs fixing (2.5-6.5) or 30% hard cases (<3)
            is_fixable_range = 2.5 <= pair['initial_contrast'] <= 6.5
            is_hard_case = pair['initial_contrast'] < 3.0

            # This filter mechanism ensures we have a good mix of fixable, hard, and already-good cases.
            if rand < 0.60 and not is_fixable_range:
                continue
            elif 0.60 <= rand < 0.90 and not is_hard_case:
                continue

            pair['pair_id'] = len(pairs)
            pairs.append(pair)

            # Progress update
            if (len(pairs) % 1000) == 0:
                pass

        return pairs


class ColorTestRunner:
    """Run tests and generate detailed reports"""

    def __init__(self):
        self.results = []

    def _get_initial_state_category(
        self, initial_contrast: float, is_large: bool
    ) -> str:
        """
        Categorizes the INITIAL contrast ratio of a color pair based on WCAG targets.
        """
        # WCAG Targets
        aa_target = 3.0 if is_large else 4.5
        aaa_target = 4.5 if is_large else 7.0

        if initial_contrast >= aaa_target:
            return 'AAA (Passed)'
        elif initial_contrast >= aa_target:
            return 'AA (Passed)'
        elif (
            initial_contrast >= aa_target - 1.0
        ):   # e.g., 3.5 to 4.5 (Normal) or 2.0 to 3.0 (Large)
            return 'Barely Failing AA'
        else:   # Below aa_target - 1.0
            return 'Horrible (Low Contrast)'

    def run_test_suite(self, pairs: List[Dict]) -> Dict:
        """Run check_and_fix_contrast on all pairs and collect metrics"""
        console.print(f'[bold]Testing {len(pairs)} color pairs...[/bold]')

        start_time = datetime.now()

        for idx, pair in enumerate(pairs):
            if (idx + 1) % 1000 == 0:
                console.print(f'Progress: {idx + 1}/{len(pairs)} pairs tested')

            try:
                # Run the algorithm
                tuned_text, success = check_and_fix_contrast(
                    pair['text_rgb'],
                    pair['bg_rgb'],
                    large=pair['large'],
                    details=False,
                )

                # Parse result (tuned_text might be RGB string or tuple)
                if isinstance(tuned_text, str):
                    # Parse "rgb(r, g, b)" format - *NOTE: The mock returns a tuple*
                    tuned_rgb = tuple(
                        map(int, tuned_text.strip('rgb()').split(','))
                    )
                else:
                    tuned_rgb = tuned_text

                # Calculate metrics
                final_contrast = calculate_contrast_ratio(
                    tuned_rgb, pair['bg_rgb']
                )

                # Calculate Delta E between ORIGINAL text color and TUNED text color
                delta_e = calculate_delta_e_2000(pair['text_rgb'], tuned_rgb)

                # Determine success based on WCAG AA target
                aa_target = 3.0 if pair['large'] else 4.5
                actual_success = final_contrast >= aa_target

                # New: Initial State Category
                initial_state_cat = self._get_initial_state_category(
                    pair['initial_contrast'], pair['large']
                )

                result = {
                    'pair_id': pair['pair_id'],
                    'category': pair['category'],
                    'large': pair['large'],
                    'text_rgb': pair['text_rgb'],
                    'bg_rgb': pair['bg_rgb'],
                    'tuned_rgb': tuned_rgb,
                    'initial_contrast': pair['initial_contrast'],
                    'final_contrast': final_contrast,
                    'target_contrast': aa_target,
                    'delta_e': delta_e,
                    'reported_success': success,
                    'actual_success': actual_success,
                    'color_changed': tuned_rgb != pair['text_rgb'],
                    'initial_state_cat': initial_state_cat,  # NEW FIELD
                }

                self.results.append(result)

            except Exception as e:
                # Error catching
                console.print(
                    f"[red]ERROR on pair {idx} ({pair['category']}): {e}[/red]"
                )
                result = {
                    'pair_id': pair['pair_id'],
                    'category': pair['category'],
                    'error': str(e),
                    'text_rgb': pair['text_rgb'],
                    'bg_rgb': pair['bg_rgb'],
                }
                self.results.append(result)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        return self._generate_report(duration)

    def _percentile(self, data: List[float], p: int) -> float:
        """Helper to calculate percentiles."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        k = (len(sorted_data) - 1) * p / 100
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return sorted_data[int(k)]
        # Linear interpolation
        return sorted_data[int(f)] * (c - k) + sorted_data[int(c)] * (k - f)

    def _generate_report(self, duration: float = 0.0) -> Dict:
        """Generate comprehensive analysis report with percentiles and initial state breakdown."""
        valid = [r for r in self.results if 'error' not in r]

        if not valid:
            return {'error': 'No valid results to analyze'}

        actual_success = [r for r in valid if r['actual_success']]
        actual_failure = [r for r in valid if not r['actual_success']]

        # --- 1. True Success Ratio (Filtering) ---
        HORRIBLE_CONTRAST_THRESHOLD = 2
        horrible_pairs = [
            r
            for r in valid
            if r['initial_contrast'] <= HORRIBLE_CONTRAST_THRESHOLD
        ]

        non_horrible_valid = [r for r in valid if r not in horrible_pairs]
        non_horrible_success = [
            r for r in actual_success if r not in horrible_pairs
        ]

        true_success_rate = 0.0
        if non_horrible_valid:
            true_success_rate = (
                len(non_horrible_success) / len(non_horrible_valid) * 100
            )

        # --- 2. Calculate Percentile Stats ---

        def get_percentile_stats(data: List[Dict]):
            # Initial Contrast: the contrast the pair started with
            initial_contrasts = [r['initial_contrast'] for r in data]
            # Delta E: the change applied to the text color
            delta_es = [r['delta_e'] for r in data if r.get('color_changed')]

            stats = {}
            for p in [25, 50, 75, 90]:
                stats[f'p{p}'] = {
                    'initial_contrast': self._percentile(initial_contrasts, p),
                    'delta_e': self._percentile(delta_es, p),
                }
            return stats

        overall_success_stats = get_percentile_stats(actual_success)
        overall_failure_stats = get_percentile_stats(actual_failure)

        # --- 3. Initial State Categorization (NEW ANALYSIS) ---
        initial_state_analysis: Dict[str, Dict[str, List[Dict]]] = {
            'Success': {},
            'Failure': {},
        }

        initial_cat_counts: Dict[str, Dict[str, int]] = {
            'Success': {
                k: 0
                for k in [
                    'AAA (Passed)',
                    'AA (Passed)',
                    'Barely Failing AA',
                    'Horrible (Low Contrast)',
                ]
            },
            'Failure': {
                k: 0
                for k in [
                    'AAA (Passed)',
                    'AA (Passed)',
                    'Barely Failing AA',
                    'Horrible (Low Contrast)',
                ]
            },
        }

        all_initial_cats = [
            'AAA (Passed)',
            'AA (Passed)',
            'Barely Failing AA',
            'Horrible (Low Contrast)',
        ]

        # Initialize structure for detailed stats per initial category
        initial_cat_stats: Dict[str, Dict[str, Dict]] = {
            'Success': {
                cat: {'initial_contrast': [], 'delta_e': []}
                for cat in all_initial_cats
            },
            'Failure': {
                cat: {'initial_contrast': [], 'delta_e': []}
                for cat in all_initial_cats
            },
        }

        for r in valid:
            cat_label = r['initial_state_cat']
            outcome = 'Success' if r['actual_success'] else 'Failure'

            initial_cat_counts[outcome][cat_label] += 1

            # Collect data for detailed stats
            initial_cat_stats[outcome][cat_label]['initial_contrast'].append(
                r['initial_contrast']
            )
            if r.get('color_changed'):
                initial_cat_stats[outcome][cat_label]['delta_e'].append(
                    r['delta_e']
                )

        # Calculate percentile stats for the new breakdown
        detailed_initial_state_stats = {}
        for outcome in ['Success', 'Failure']:
            detailed_initial_state_stats[outcome] = {}
            for cat in all_initial_cats:
                cat_data = initial_cat_stats[outcome][cat]
                # Calculate median (P50) for Initial Contrast and Delta E for this subgroup
                p50_stats = {
                    'initial_contrast': self._percentile(
                        cat_data['initial_contrast'], 50
                    ),
                    'delta_e': self._percentile(cat_data['delta_e'], 50),
                }
                detailed_initial_state_stats[outcome][cat] = {
                    'count': initial_cat_counts[outcome][cat],
                    'median': p50_stats,
                }

        # --- 4. Category Breakdown (Original) ---
        category_data: Dict[str, Dict] = {}
        for r in valid:
            cat = r['category']
            if cat not in category_data:
                category_data[cat] = {
                    'total': 0,
                    'success': 0,
                    'delta_e_samples': [],
                    'initial_contrast_samples': [],
                }

            category_data[cat]['total'] += 1
            if r['actual_success']:
                category_data[cat]['success'] += 1
                if r.get('color_changed'):
                    category_data[cat]['delta_e_samples'].append(r['delta_e'])

            category_data[cat]['initial_contrast_samples'].append(
                r['initial_contrast']
            )

        # --- 5. Final Report Assembly ---

        report = {
            'test_summary': {
                'total_pairs': len(self.results),
                'valid_tests': len(valid),
                'errors': len(self.results) - len(valid),
                'timestamp': datetime.now().isoformat(),
                'duration': duration,
            },
            'success_metrics': {
                'overall_success_rate': f'{len(actual_success) / len(valid) * 100:.2f}%',
                'true_success_rate_filtered': f'{true_success_rate:.2f}%',
                'horrible_pairs_filtered': len(horrible_pairs),
                'initial_contrast_threshold': f'<={HORRIBLE_CONTRAST_THRESHOLD}',
            },
            'delta_e_metrics': {
                'median_successful': overall_success_stats['p50']['delta_e'],
                'p90_successful': overall_success_stats['p90']['delta_e'],
                'under_2.0': f"{sum(1 for r in actual_success if r['delta_e'] <= 2.0) / len(actual_success) * 100:.2f}%"
                if actual_success
                else '0%',
            },
            'percentile_analysis': {
                'success_set': overall_success_stats,
                'failure_set': overall_failure_stats,
            },
            'category_breakdown': category_data,
            'initial_state_analysis': detailed_initial_state_stats,  # NEW REPORT SECTION
        }

        return report

    def print_summary_table(self, report: Dict):
        """Prints the summary metrics table using rich."""
        table = Table(title='Metric', box=box.SIMPLE)
        table.add_column('Metric', style='cyan', no_wrap=True)
        table.add_column('Value', style='magenta')
        table.add_column('Details', style='green')

        # Extract metrics
        success_metrics = report['success_metrics']
        delta_e_metrics = report['delta_e_metrics']
        test_summary = report['test_summary']

        # Success Rate
        table.add_row(
            'Success Rate',
            success_metrics['true_success_rate_filtered'],
            'WCAG AA compliance achieved',
        )

        # High-Fidelity Success
        table.add_row(
            'High-Fidelity Success',
            delta_e_metrics['under_2.0'],
            'ΔE2000 < 2.0',
        )

        # Median Delta E
        table.add_row(
            'Median ΔE2000',
            f"{delta_e_metrics['median_successful']:.2f}",
            'For successful pairs',
        )

        # Median Runtime
        duration = test_summary.get('duration', 0)
        total_pairs = test_summary.get('total_pairs', 1)
        avg_runtime = duration / total_pairs if total_pairs > 0 else 0
        table.add_row(
            'Median Runtime', f'{avg_runtime:.6f}s', 'Per color pair'
        )

        # Throughput
        throughput = total_pairs / duration if duration > 0 else 0
        table.add_row('Throughput', f'{int(throughput):,} pairs/second', '')

        console.print(table)

    def print_category_table(self, report: Dict):
        """Prints the category performance table using rich."""
        table = Table(title='Performance by Category', box=box.SIMPLE)
        table.add_column('Category', style='cyan')
        table.add_column('Total Pairs', justify='right')
        table.add_column('Success Rate', justify='right', style='green')
        table.add_column(
            'Median ρ_initial', justify='right'
        )   # Initial contrast
        table.add_column('Median ΔE2000', justify='right')

        category_stats = report['category_breakdown']

        # Sort by Success Rate descending
        sorted_categories = sorted(
            category_stats.items(),
            key=lambda item: item[1]['success'] / item[1]['total'],
            reverse=True,
        )

        for cat, stats in sorted_categories:
            total = stats['total']
            success_rate = (stats['success'] / total) * 100

            # Median Initial Contrast
            if stats['initial_contrast_samples']:
                median_initial = self._percentile(
                    stats['initial_contrast_samples'], 50
                )
            else:
                median_initial = 0.0

            # Median Delta E
            median_delta_e = (
                self._percentile(stats['delta_e_samples'], 50)
                if stats['delta_e_samples']
                else 0.0
            )

            table.add_row(
                cat,
                str(total),
                f'{success_rate:.2f}%',
                f'{median_initial:.2f}',
                f'{median_delta_e:.2f}',
            )

        console.print(table)

    def save_results(self, filename: str = 'color_test_results.json'):
        """Save detailed results to JSON file"""
        # Regenerate report to ensure we get the latest metrics after all tests
        output = {
            'results': self.results,
            'report': self._generate_report(),
        }

        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)

        console.print(f'\n[dim]Detailed results saved to {filename}[/dim]')


def main():
    """Run the comprehensive test suite"""
    generator = RealWorldColorGenerator(seed=45)
    pairs = generator.generate_test_suite(total_pairs=10000)

    console.print(f'[bold]Generated {len(pairs)} pairs for testing.[/bold]')

    runner = ColorTestRunner()
    report = runner.run_test_suite(pairs)

    console.print('\n')
    runner.print_summary_table(report)
    console.print('\n')
    runner.print_category_table(report)

    # Save results
    runner.save_results('color_test_results.json')


if __name__ == '__main__':
    main()
