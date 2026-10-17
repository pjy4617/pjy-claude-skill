---
name: Kinetic Horizon
colors:
  surface: '#fff8f5'
  surface-dim: '#e0d8d5'
  surface-bright: '#fff8f5'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#faf2ee'
  surface-container: '#f4ece8'
  surface-container-high: '#eee7e3'
  surface-container-highest: '#e9e1dd'
  on-surface: '#1e1b19'
  on-surface-variant: '#564336'
  inverse-surface: '#33302d'
  inverse-on-surface: '#f7efeb'
  outline: '#8a7264'
  outline-variant: '#ddc1b0'
  surface-tint: '#964900'
  primary: '#964900'
  on-primary: '#ffffff'
  primary-container: '#f58220'
  on-primary-container: '#5b2a00'
  inverse-primary: '#ffb786'
  secondary: '#815600'
  on-secondary: '#ffffff'
  secondary-container: '#ffae00'
  on-secondary-container: '#6a4600'
  tertiary: '#775a00'
  on-tertiary: '#ffffff'
  tertiary-container: '#c99a00'
  on-tertiary-container: '#483500'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdcc6'
  primary-fixed-dim: '#ffb786'
  on-primary-fixed: '#311300'
  on-primary-fixed-variant: '#723600'
  secondary-fixed: '#ffddb1'
  secondary-fixed-dim: '#ffba48'
  on-secondary-fixed: '#291800'
  on-secondary-fixed-variant: '#614000'
  tertiary-fixed: '#ffdf99'
  tertiary-fixed-dim: '#f6bf22'
  on-tertiary-fixed: '#251a00'
  on-tertiary-fixed-variant: '#5a4300'
  background: '#fff8f5'
  on-background: '#1e1b19'
  surface-variant: '#e9e1dd'
typography:
  display-hero:
    fontFamily: Outfit
    fontSize: 56px
    fontWeight: '700'
    lineHeight: 64px
    letterSpacing: -0.03em
  display-hero-mobile:
    fontFamily: Outfit
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Outfit
    fontSize: 40px
    fontWeight: '600'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Outfit
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Outfit
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Outfit
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 30px
    letterSpacing: 0em
  title-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
    letterSpacing: 0em
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
    letterSpacing: 0em
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: 0em
  body-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.06em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.5rem
  margin: 2rem
  gutter-desktop: 2rem
  margin-desktop: 5rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

This design system expresses a forward-looking, high-trust technology aesthetic that marries energetic warmth with enterprise precision. Built upon the core pillars of Team, Trust, and Technology, the visual language balances human warmth with technical authority. 

The aesthetic is Modern Corporate infused with luminous kinetic energy. Rather than adopting cold, sterile tech blues, this system leans into radiating solar tones—golden oranges, luminous amber gradients, and subtle vector trajectories—grounded by pure optical white planes and high-density warm charcoal typography. The interface evokes optimism, momentum, enterprise stability, and collaborative clarity.

## Colors

The palette establishes an unmistakable, warm radiance while maintaining rigorous enterprise legibility standards.

- **Primary (`#F58220`)**: The core brand anchor. Used for primary CTAs, active states, key data markers, and foundational branding accents.
- **Secondary (`#FFAE00`)**: The transitional amber tone that fuels radiant gradients, highlight indicators, and focal metric cards.
- **Tertiary (`#FFC72C`)**: The luminous apex color used for subtle ambient glows, hover shimmer accents, badges, and progress fills.
- **Neutral (`#1C1917`)**: A deep, warm carbon stone that replaces pure black to prevent harsh glare while guaranteeing maximum contrast (WCAG AAA compliant against white and soft cream surfaces).

### Supporting Roles
- **Canvas Base**: Pure `#FFFFFF` serves as the primary stage to maintain an airy, immaculate presentation feel.
- **Surface Muted**: `#FBF8F5` provides warm, grounded card fills and grouped container backdrops.
- **Border Subtle**: `#EAE2DA` forms delicate structural perimeters that harmonize with the warm undertones.
- **Gradients**: Linear and radial sweeps between `#F58220` and `#FFAE00` (often terminating into `#FFC72C` ambient feathering) recreate the kinetic solar atmosphere of the presentation templates.

## Typography

Typography pairs **Outfit** for structural headings with **Plus Jakarta Sans** for interfaces and narrative body copy. 

- **Outfit** carries geometric precision and modern architectural cadence. Its balanced letterforms echo the crisp curves of the brand mark, providing high impact across presentation hero frames and section dividers.
- **Plus Jakarta Sans** features subtle humanist warmth and open counters, maintaining effortless scannability across enterprise dashboards, complex documentation, and technical slides.
- Uppercase styling is reserved strictly for `label-sm` category badges and metric identifiers, balanced with wide tracking (`0.06em`) for elevated sophistication.

## Layout & Spacing

The layout is built on a 12-column fluid grid system engineered for wide-format presentations (16:9 ratio) and high-density enterprise web applications.

- **Desktop (1024px+)**: 12 columns with 32px (`gutter-desktop`) spacing and 80px (`margin-desktop`) outer canvas padding. Sections embrace generous vertical breathing room (80px to 120px) to mirror the expansive white band found in the brand slides.
- **Tablet (768px - 1023px)**: 8 columns with 24px gutters and 32px outer margins. Multi-column cards collapse from 4-across to 2-across layouts.
- **Mobile (320px - 767px)**: 4 columns with 16px gutters and 16px margins. Hero presentation stages convert horizontal banner arrangements into stacked vertical flows.

A strict 8pt rhythm governs internal component padding and stack gaps, preventing visual clutter and ensuring systematic alignment between content modules.

## Elevation & Depth

Elevation departs from cold, heavy black drop shadows, relying instead on warm solar-tinted diffusion, crisp architectural borders, and intentional layer stacking:

- **Flat / Base Layer**: `#FFFFFF` canvas grounded on subtle perimeter hairline dividers (`1px solid #EAE2DA`).
- **Elevated Card (Level 1)**: Pure white background accompanied by an ultra-soft amber-tinted shadow (`0 4px 20px -2px rgba(245, 130, 32, 0.08), 0 2px 6px -1px rgba(28, 25, 23, 0.04)`).
- **Interactive / Hover (Level 2)**: Translates upward by 2px with an intensified amber glow (`0 12px 32px -4px rgba(245, 130, 32, 0.16), 0 4px 12px -2px rgba(28, 25, 23, 0.06)`).
- **Floating Overlays & Menus (Level 3)**: Frosted translucent layer (`rgba(255, 255, 255, 0.92)` with `16px` backdrop-filter blur) flanked by an outer radiant spread (`0 20px 48px -6px rgba(28, 25, 23, 0.12)`).
- **Linear Horizon Accents**: White or translucent curved vector lines (0.5px to 1.5px stroke at 40-70% opacity) slice horizontally across radiant orange background banners to deliver the signature kinetic motion seen in the branded slides.

## Shapes

The shape system employs roundedness level 2 (0.5rem / 8px core radius), balancing approachable corporate warmth with structural modernism:

- **Standard Elements (0.5rem / 8px)**: Input fields, standard buttons, dropdown menus, and utility cards.
- **Medium Panels (`rounded-lg` / 1rem / 16px)**: Dashboard feature cards, modal dialogs, and slide callout containers.
- **Hero Containers (`rounded-xl` / 1.5rem / 24px)**: Presentation stage wraps, radiant banners, and primary marketing highlights.
- **Pill Badges (`9999px`)**: Status pills, category chips, and numeric indices (such as the superscript indicator in the brand mark) remain full-capsule shapes.

## Components

### Buttons
- **Primary**: Rich gradient fill (`linear-gradient(135deg, #F58220 0%, #FFAE00 100%)`) with white text, font weight 600, 8px corner radius, and an ambient warm shadow (`0 4px 14px rgba(245, 130, 32, 0.35)`). Hover state brightens toward the tertiary yellow apex.
- **Secondary**: Pure `#FFFFFF` background with a 1.5px border in `#F58220`, orange text, and subtle warm neutral fill (`#FBF8F5`) on hover.
- **Ghost / Text**: Transparent background, dark neutral text (`#1C1917`), transitioning to `#F58220` text with a faint `#FFF5EB` back-plate on hover.

### Chips & Tags
- **Category Badge**: Pill-shaped (`rounded-full`), padded 4px 12px, font size 11px uppercase. Background uses a gentle 10% tint of `#F58220` (`#FFF3E8`) paired with `#D0660D` dark orange text for optimal accessibility.
- **Metric Pill**: Emulates the numeric brand badge with a radiant circular or pill container, white bold text, and a micro drop shadow.

### Cards
- **Presentation Cards**: Crisp `#FFFFFF` surface, 16px radius, enclosed by a thin `#EAE2DA` border. On hover, the top border or accent bar illuminates with the signature orange-to-yellow gradient strip (3px height).
- **Radiant Hero Banners**: Saturated `#F58220` to `#FFAE00` fluid background featuring delicate intersecting white trajectory curves and crisp white headline typography.

### Input Fields
- **Default State**: 8px radius, height 44px, `#FFFFFF` fill, 1px border in `#EAE2DA`, text in `#1C1917`.
- **Focus State**: Border transitions to `#F58220`, reinforced with a soft 3px outer glow ring (`rgba(245, 130, 32, 0.20)`).

### Selection Controls (Checkboxes & Radios)
- **Checkboxes**: 20x20px box with 4px radius. Unchecked state uses a 1.5px border in `#C8BFB6`. Checked state fills with `#F58220` and displays a crisp white check vector.
- **Radio Buttons**: Concentric circles; selected state features an outer `#F58220` ring surrounding an 8px solid orange center disc cushioned by a 2px white gap.

### Lists & Navigation
- **Navigation Links**: Clean text links in `#1C1917` with an active bottom-bar indicator (2px height) rendered in the primary orange gradient.
- **Feature Bullet Lists**: Custom vector checkmarks or amber gradient dots replace standard browser bullets, reinforced by 16px vertical list row separation.