<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport"
        content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">
    <title>RubyBet</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        charcoal: '#121212',
                        surface: '#1E1E1E',
                        surface2: '#2A2A2A',
                        ruby: '#E31E24',
                        'ruby-dark': '#B91820',
                    },
                    boxShadow: {
                        'ruby': '0 0 20px rgba(227,30,36,0.4)',
                    }
                }
            }
        }
    </script>
    <link
        href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800;900&family=Inter:wght@400;500;600;700&display=swap"
        rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap"
        rel="stylesheet">
    <style>
        :root {
            --bg: #121212;
            --surface: #1E1E1E;
            --surface2: #2A2A2A;
            --surface3: #333;
            --red: #E31E24;
            --red-dark: #B91820;
            --red-glow: rgba(227, 30, 36, 0.4);
            --text: #F5F5F5;
            --dim: #9CA3AF;
            --dim2: #6B7280;
            --border: #333;
            --green: #22C55E;
            --green-dim: #166534;
            --gold: #FFD700;
            --blue: #3B82F6;
            --radius: 12px;
            --radius-lg: 16px;
            --radius-xl: 20px;
            --nav-h: 68px;
            --header-h: 56px;
            --tg-safe-top: env(safe-area-inset-top, 0px);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-tap-highlight-color: transparent
        }

        body {
            background: var(--bg);
            color: var(--text);
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
            overflow-x: hidden;
            padding-bottom: calc(var(--nav-h) + 12px);
            overscroll-behavior: none;
        }

        ::-webkit-scrollbar {
            width: 3px
        }

        ::-webkit-scrollbar-track {
            background: transparent
        }

        ::-webkit-scrollbar-thumb {
            background: #333;
            border-radius: 3px
        }

        h1,
        h2,
        h3,
        .font-display {
            font-family: 'Montserrat', sans-serif
        }

        ::selection {
            background: var(--red);
            color: #fff
        }

        /* === FORTUNE WHEEL === */
        .wh-bulb {
            position: absolute;
            width: 6px;
            height: 6px;
            background: #fff;
            border-radius: 50%;
            box-shadow: 0 0 8px #fff, 0 0 15px #e31c23;
            z-index: 10
        }

        .wh-seg {
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            z-index: 10
        }

        .wh-seg-inner {
            position: absolute;
            left: -40px;
            top: -125px;
            width: 80px;
            height: 80px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center
        }

        .wh-seg-label {
            font-family: 'Montserrat', sans-serif;
            font-size: 11px;
            font-weight: 900;
            color: #fff;
            text-transform: uppercase;
            letter-spacing: 1px;
            text-shadow: 0 1px 3px rgba(0, 0, 0, .6);
            margin-top: 2px
        }

        @keyframes wheel-glow {

            0%,
            100% {
                box-shadow: 0 0 8px #fff, 0 0 15px #e31c23
            }

            50% {
                box-shadow: 0 0 12px #fff, 0 0 25px #e31c23, 0 0 35px rgba(227, 28, 35, .4)
            }
        }

        .wh-bulb {
            animation: wheel-glow 1.5s ease-in-out infinite alternate
        }

        /* === LIVE DROPS === */
        .live-drops-section {
            padding: 0 16px;
            margin-bottom: 16px
        }

        .live-drops-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 10px
        }

        .live-drops-dot {
            width: 8px;
            height: 8px;
            background: #e31c23;
            border-radius: 50%;
            box-shadow: 0 0 6px #e31c23;
            animation: pulse-dot 2s infinite
        }

        .live-drops-title {
            font-family: 'Montserrat', sans-serif;
            font-size: 12px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--dim)
        }

        .live-drops-scroll {
            display: flex;
            gap: 10px;
            overflow-x: auto;
            -ms-overflow-style: none;
            scrollbar-width: none;
            padding-bottom: 4px
        }

        .live-drops-scroll::-webkit-scrollbar {
            display: none
        }

        .live-drop-card {
            flex-shrink: 0;
            width: 160px;
            padding: 10px 12px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            position: relative;
            overflow: hidden;
            transition: border-color .2s
        }

        .live-drop-card::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 2px;
            background: rgba(227, 30, 36, .3)
        }

        .live-drop-card.big::after {
            height: 2px;
            background: var(--red);
            box-shadow: 0 0 10px rgba(227, 28, 35, .5)
        }

        .live-drop-user {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 6px
        }

        .live-drop-avatar {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: var(--surface2);
            border: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            font-weight: 700;
            color: var(--dim);
            overflow: hidden
        }

        .live-drop-avatar img {
            width: 100%;
            height: 100%;
            object-fit: cover
        }

        .live-drop-name {
            font-size: 12px;
            font-weight: 600;
            color: var(--dim);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 90px
        }

        .live-drop-amount {
            font-family: 'Montserrat', sans-serif;
            font-size: 14px;
            font-weight: 800;
            color: var(--red)
        }

        .live-drop-game {
            font-size: 10px;
            color: var(--dim2);
            margin-top: 2px
        }

        /* === SCREENS === */
        .screen {
            display: none;
            opacity: 0;
            transition: opacity .15s ease
        }

        .screen.active {
            display: block;
            opacity: 1
        }

        /* === HEADER === */
        .header {
            position: sticky;
            top: 0;
            z-index: 50;
            background: var(--bg);
            border-bottom: 1px solid rgba(255, 255, 255, .05);
            padding: 10px 16px;
            padding-top: calc(var(--tg-safe-top) + 10px);
            display: flex;
            align-items: center;
            justify-content: space-between;
            min-height: var(--header-h);
            backdrop-filter: blur(12px)
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 6px
        }

        .logo-icon {
            width: 32px;
            height: 32px;
            background: var(--red);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 12px var(--red-glow)
        }

        .logo-icon .material-symbols-outlined {
            color: #fff;
            font-size: 18px
        }

        .logo-text {
            font-family: 'Montserrat', sans-serif;
            font-weight: 800;
            font-size: 18px;
            letter-spacing: .5px;
            color: #fff
        }

        .logo-text span {
            color: var(--red)
        }

        .header-right {
            display: flex;
            align-items: center;
            gap: 8px
        }

        .header-bal {
            display: flex;
            align-items: center;
            gap: 6px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 5px 12px 5px 8px;
            font-weight: 600;
            font-size: 13px;
            color: #fff;
            cursor: pointer
        }

        .header-bal .amt {
            color: var(--red);
            font-weight: 700;
            font-family: 'Montserrat', sans-serif;
            font-size: 11px;
            margin-left: 2px
        }

        .header-notif {
            position: relative;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: var(--surface);
            border: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer
        }

        .header-notif .material-symbols-outlined {
            font-size: 18px;
            color: var(--dim)
        }

        .header-notif .dot {
            position: absolute;
            top: 6px;
            right: 6px;
            width: 7px;
            height: 7px;
            background: var(--red);
            border-radius: 50%;
            box-shadow: 0 0 6px var(--red)
        }

        /* === BOTTOM NAV === */
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: var(--nav-h);
            background: var(--surface);
            border-top: 1px solid rgba(255, 255, 255, .05);
            display: flex;
            z-index: 100;
            padding-bottom: env(safe-area-inset-bottom);
            box-shadow: 0 -4px 20px rgba(0, 0, 0, .4)
        }

        .nav-item {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 3px;
            cursor: pointer;
            color: var(--dim);
            transition: color .2s;
            position: relative
        }

        .nav-item.active {
            color: var(--red)
        }

        .nav-item .material-symbols-outlined {
            font-size: 22px;
            transition: all .2s
        }

        .nav-item.active .material-symbols-outlined {
            filter: drop-shadow(0 0 6px var(--red-glow))
        }

        .nav-item .nav-label {
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: .5px
        }

        .nav-item .nav-label {
            font-size: 9px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: .8px;
            font-family: 'Montserrat', sans-serif
        }

        /* === SHARED UI === */
        .section {
            padding: 0 16px;
            margin-bottom: 20px
        }

        .section-head {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px
        }

        .section-title {
            font-family: 'Montserrat', sans-serif;
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--dim)
        }

        .section-more {
            font-size: 11px;
            font-weight: 700;
            color: var(--red);
            cursor: pointer;
            text-transform: uppercase;
            letter-spacing: .5px
        }

        .card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            overflow: hidden
        }

        .btn-primary {
            width: 100%;
            height: 48px;
            border-radius: var(--radius);
            border: none;
            background: var(--red);
            color: #fff;
            font-family: 'Montserrat', sans-serif;
            font-weight: 700;
            font-size: 14px;
            letter-spacing: .5px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            box-shadow: 0 4px 16px var(--red-glow);
            transition: all .15s;
            text-transform: uppercase
        }

        .btn-primary:active {
            transform: scale(.97);
            filter: brightness(.9)
        }

        .btn-outline {
            width: 100%;
            height: 48px;
            border-radius: var(--radius);
            border: 1.5px solid var(--red);
            background: transparent;
            color: var(--red);
            font-family: 'Montserrat', sans-serif;
            font-weight: 700;
            font-size: 14px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: all .15s;
            text-transform: uppercase
        }

        .btn-outline:active {
            background: rgba(227, 30, 36, .08);
            transform: scale(.97)
        }

        .pill-row {
            display: flex;
            gap: 8px;
            overflow-x: auto;
            padding: 0 16px 12px;
            -ms-overflow-style: none;
            scrollbar-width: none
        }

        .pill-row::-webkit-scrollbar {
            display: none
        }

        .pill {
            height: 34px;
            padding: 0 16px;
            border-radius: 17px;
            border: 1px solid var(--border);
            background: var(--surface);
            color: var(--dim);
            font-size: 12px;
            font-weight: 600;
            white-space: nowrap;
            cursor: pointer;
            display: flex;
            align-items: center;
            transition: all .15s;
            flex-shrink: 0
        }

        .pill.active {
            background: var(--red);
            color: #fff;
            border-color: var(--red);
            box-shadow: 0 2px 10px var(--red-glow)
        }

        .pill:active {
            transform: scale(.95)
        }

        .divider {
            height: 1px;
            background: var(--border);
            margin: 0 16px
        }

        /* ======================== */
        /* === LOBBY SCREEN === */
        /* ======================== */
        .lobby-search {
            margin: 12px 16px;
            display: flex;
            align-items: center;
            gap: 10px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 10px 14px;
            cursor: pointer
        }

        .lobby-search .material-symbols-outlined {
            color: var(--dim);
            font-size: 20px
        }

        .lobby-search span {
            color: var(--dim2);
            font-size: 13px;
            font-weight: 500
        }

        /* Hero Banner */
        .hero-banner {
            margin: 0 16px 16px;
            border-radius: var(--radius-xl);
            background: linear-gradient(135deg, #1a0000, #3a0a0a 50%, #0a0000);
            border: 1.5px solid rgba(227, 30, 36, .3);
            padding: 24px 20px;
            position: relative;
            overflow: hidden;
            min-height: 140px;
            box-shadow: 0 0 20px rgba(227, 30, 36, .1)
        }

        .hero-banner::after {
            content: '';
            position: absolute;
            top: -50%;
            right: -20%;
            width: 200px;
            height: 200px;
            background: radial-gradient(circle, rgba(227, 30, 36, .15), transparent 70%);
            border-radius: 50%
        }

        .hero-tag {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-size: 10px;
            font-weight: 800;
            text-transform: uppercase;
            color: #fff;
            background: var(--red);
            padding: 3px 8px;
            border-radius: 4px;
            margin-bottom: 10px;
            letter-spacing: 1px
        }

        .hero-tag .material-symbols-outlined {
            font-size: 12px
        }

        .hero-title {
            font-family: 'Montserrat', sans-serif;
            font-size: 28px;
            font-weight: 900;
            line-height: 1.15;
            margin-bottom: 4px;
            letter-spacing: -.5px
        }

        .hero-title .accent {
            color: var(--red);
            text-shadow: 0 0 20px var(--red-glow)
        }

        .hero-sub {
            font-size: 12px;
            color: var(--dim);
            margin-bottom: 16px
        }

        .hero-actions {
            display: flex;
            gap: 10px;
            position: relative;
            z-index: 1
        }

        .hero-actions .hero-btn {
            height: 38px;
            padding: 0 20px;
            border-radius: 10px;
            border: none;
            font-family: 'Montserrat', sans-serif;
            font-weight: 700;
            font-size: 12px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all .15s;
            text-transform: uppercase;
            letter-spacing: .5px
        }

        .hero-actions .hero-btn:active {
            transform: scale(.95)
        }

        .hero-btn.filled {
            background: var(--red);
            color: #fff;
            box-shadow: 0 2px 12px var(--red-glow)
        }

        .hero-btn.ghost {
            background: rgba(255, 255, 255, .08);
            color: #fff;
            border: 1px solid rgba(255, 255, 255, .12)
        }

        /* Wheel Banner */
        .wheel-banner {
            margin: 0 16px 16px;
            border-radius: var(--radius-lg);
            background: linear-gradient(135deg, #1a0a0a, #2a0a0a);
            border: 1px solid rgba(227, 30, 36, .25);
            padding: 14px 16px;
            display: flex;
            align-items: center;
            gap: 12px;
            cursor: pointer;
            transition: transform .15s;
            box-shadow: 0 0 15px rgba(227, 30, 36, .08)
        }

        .wheel-banner:active {
            transform: scale(.97)
        }

        .wheel-icon {
            font-size: 32px;
            animation: wrot 3s linear infinite
        }

        @keyframes wrot {
            0% {
                transform: rotate(0)
            }

            100% {
                transform: rotate(360deg)
            }
        }

        .wheel-banner.done {
            opacity: .5
        }

        .wheel-banner.done .wheel-icon {
            animation: none
        }

        .wheel-info h3 {
            font-size: 13px;
            font-weight: 700;
            color: #fff;
            font-family: 'Montserrat', sans-serif
        }

        .wheel-info p {
            font-size: 11px;
            color: var(--dim)
        }

        /* VIP Progress */
        .vip-strip {
            margin: 0 16px 16px;
            display: flex;
            align-items: center;
            gap: 12px
        }

        .vip-strip-info {
            flex: 1
        }

        .vip-strip-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px
        }

        .vip-strip-name {
            font-size: 10px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--dim);
            font-family: 'Montserrat', sans-serif
        }

        .vip-strip-pct {
            font-size: 10px;
            font-weight: 700;
            color: var(--red)
        }

        .vip-bar {
            height: 6px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 3px;
            overflow: hidden
        }

        .vip-bar-fill {
            height: 100%;
            background: var(--red);
            border-radius: 3px;
            transition: width .6s;
            box-shadow: 0 0 8px var(--red-glow)
        }

        /* Categories */
        .cat-row {
            display: flex;
            gap: 12px;
            padding: 0 16px;
            margin-bottom: 20px;
            overflow-x: auto;
            -ms-overflow-style: none;
            scrollbar-width: none
        }

        .cat-row::-webkit-scrollbar {
            display: none
        }

        .cat-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 6px;
            cursor: pointer;
            flex-shrink: 0
        }

        .cat-icon {
            width: 56px;
            height: 56px;
            border-radius: var(--radius);
            background: var(--surface);
            border: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all .15s
        }

        .cat-icon .material-symbols-outlined {
            font-size: 24px;
            color: var(--red)
        }

        .cat-item:active .cat-icon {
            border-color: var(--red);
            background: rgba(227, 30, 36, .08)
        }

        .cat-label {
            font-size: 10px;
            font-weight: 600;
            color: var(--dim);
            text-transform: uppercase;
            letter-spacing: .5px
        }

        /* Game Grid */
        .game-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            padding: 0 16px;
            margin-bottom: 20px
        }

        /* === SEARCH OVERLAY === */
        .search-overlay {
            position: fixed;
            inset: 0;
            z-index: 250;
            background: var(--bg);
            display: none;
            flex-direction: column
        }

        .search-overlay.open {
            display: flex
        }

        .search-header {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px 16px;
            border-bottom: 1px solid var(--border)
        }

        .search-input {
            flex: 1;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 10px 14px;
            color: #fff;
            font-size: 14px;
            outline: none;
            font-family: Inter, sans-serif
        }

        .search-input:focus {
            border-color: var(--red)
        }

        .search-input::placeholder {
            color: var(--dim2)
        }

        .search-results {
            flex: 1;
            overflow-y: auto;
            padding: 12px 16px
        }

        .search-result-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            margin-bottom: 8px;
            cursor: pointer;
            transition: all .15s
        }

        .search-result-item:active {
            transform: scale(.98);
            border-color: var(--red)
        }

        .search-result-icon {
            width: 44px;
            height: 44px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px
        }

        .search-result-name {
            font-size: 13px;
            font-weight: 700;
            color: #fff
        }

        .search-result-tag {
            font-size: 10px;
            color: var(--dim);
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: .5px
        }

        .search-empty {
            text-align: center;
            padding: 60px 0;
            color: var(--dim2);
            font-size: 13px
        }

        /* === TOP WINNINGS LEADERBOARD === */
        .top-wins-section {
            margin: 0 16px 20px
        }

        .top-wins-tabs {
            display: flex;
            gap: 0;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            overflow: hidden;
            margin-bottom: 12px
        }

        .tw-tab {
            flex: 1;
            padding: 8px 0;
            text-align: center;
            font-size: 10px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: .8px;
            color: var(--dim);
            cursor: pointer;
            transition: all .15s;
            border-right: 1px solid var(--border)
        }

        .tw-tab:last-child {
            border-right: none
        }

        .tw-tab.active {
            background: rgba(227, 30, 36, .08);
            color: var(--red)
        }

        .tw-row {
            display: flex;
            align-items: center;
            padding: 10px 12px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            margin-bottom: 6px;
            gap: 10px
        }

        .tw-rank {
            width: 24px;
            font-family: 'Montserrat', sans-serif;
            font-size: 14px;
            font-weight: 900;
            color: var(--dim)
        }

        .tw-rank.gold {
            color: #FFD700
        }

        .tw-rank.silver {
            color: #C0C0C0
        }

        .tw-rank.bronze {
            color: #CD7F32
        }

        .tw-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: 700;
            color: #fff
        }

        .tw-info {
            flex: 1
        }

        .tw-name {
            font-size: 12px;
            font-weight: 700;
            color: #fff
        }

        .tw-game {
            font-size: 10px;
            color: var(--dim)
        }

        .tw-amount {
            text-align: right
        }

        .tw-val {
            font-family: 'Montserrat', sans-serif;
            font-size: 13px;
            font-weight: 800;
            color: var(--green)
        }

        .tw-mult {
            font-size: 10px;
            color: var(--dim)
        }

        /* === PROVIDERS SECTION === */
        .providers-row {
            display: flex;
            gap: 8px;
            padding: 0 16px;
            overflow-x: auto;
            margin-bottom: 20px;
            -ms-overflow-style: none;
            scrollbar-width: none
        }

        .providers-row::-webkit-scrollbar {
            display: none
        }

        .provider-pill {
            flex-shrink: 0;
            padding: 8px 16px;
            border-radius: 20px;
            background: var(--surface);
            border: 1px solid var(--border);
            font-size: 11px;
            font-weight: 700;
            color: var(--dim);
            cursor: pointer;
            transition: all .15s;
            text-transform: uppercase;
            letter-spacing: .3px;
            white-space: nowrap
        }

        .provider-pill.active,
        .provider-pill:active {
            background: rgba(227, 30, 36, .08);
            border-color: var(--red);
            color: var(--red)
        }

        /* === FAVORITES HEART === */
        .fav-btn {
            position: absolute;
            top: 8px;
            right: 8px;
            z-index: 10;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: rgba(0, 0, 0, .5);
            backdrop-filter: blur(4px);
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all .15s
        }

        .fav-btn .material-symbols-outlined {
            font-size: 16px;
            color: var(--dim);
            transition: all .15s
        }

        .fav-btn.liked .material-symbols-outlined {
            color: var(--red);
            font-variation-settings: 'FILL' 1
        }

        /* === NAV BADGE === */
        .nav-badge {
            position: absolute;
            top: 2px;
            right: 50%;
            transform: translateX(calc(50% + 10px));
            min-width: 16px;
            height: 16px;
            border-radius: 8px;
            background: var(--red);
            color: #fff;
            font-size: 9px;
            font-weight: 800;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0 4px;
            box-shadow: 0 0 6px var(--red-glow)
        }

        .game-tile {
            border-radius: var(--radius-lg);
            overflow: hidden;
            background: var(--surface);
            border: 1px solid var(--border);
            cursor: pointer;
            transition: all .15s;
            position: relative
        }

        .game-tile:active {
            transform: scale(.96)
        }

        .game-tile-img {
            width: 100%;
            aspect-ratio: 4/3;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 42px;
            position: relative
        }

        .game-tile-img .badge {
            position: absolute;
            top: 8px;
            right: 8px;
            font-size: 9px;
            font-weight: 800;
            text-transform: uppercase;
            padding: 2px 8px;
            border-radius: 4px;
            letter-spacing: .5px
        }

        .badge.hot {
            background: var(--red);
            color: #fff
        }

        .badge.new {
            background: var(--green);
            color: #fff
        }

        .badge.soon {
            background: var(--surface2);
            color: var(--dim)
        }

        .game-tile-info {
            padding: 10px 12px
        }

        .game-tile-name {
            font-family: 'Montserrat', sans-serif;
            font-size: 12px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: .3px
        }

        .game-tile-tag {
            font-size: 10px;
            color: var(--dim);
            font-weight: 500;
            margin-top: 2px
        }

        /* ======================== */
        /* === GAME SCREEN === */
        /* ======================== */
        .game-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 16px
        }

        .game-back {
            display: flex;
            align-items: center;
            gap: 4px;
            cursor: pointer;
            color: var(--dim);
            font-size: 13px;
            font-weight: 600
        }

        .game-back .material-symbols-outlined {
            font-size: 20px
        }

        .game-title-bar {
            font-family: 'Montserrat', sans-serif;
            font-weight: 800;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: .5px
        }

        .game-bal {
            display: flex;
            align-items: center;
            gap: 4px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 4px 12px;
            font-weight: 700;
            font-size: 13px
        }

        .game-bal .material-symbols-outlined {
            font-size: 14px;
            color: var(--red)
        }

        /* Jackpot display */
        .jackpot-display {
            text-align: center;
            padding: 8px 0 4px
        }

        .jackpot-label {
            font-size: 9px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: var(--red)
        }

        .jackpot-amount {
            font-family: 'Montserrat', sans-serif;
            font-size: 28px;
            font-weight: 900;
            color: #fff;
            letter-spacing: -1px
        }

        .jackpot-amount span {
            color: var(--dim);
            font-size: 16px;
            font-weight: 600;
            margin-left: 4px
        }

        /* Grid */
        .grid-frame {
            margin: 0 10px;
            background: rgba(0, 0, 0, .4);
            border: 2px solid rgba(227, 30, 36, .15);
            border-radius: var(--radius-lg);
            padding: 6px;
            position: relative;
            overflow: hidden
        }

        .grid-frame.bonus-mode {
            border-color: var(--red);
            box-shadow: 0 0 30px var(--red-glow)
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 3px
        }

        .cell {
            aspect-ratio: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            border-radius: 8px;
            background: rgba(255, 255, 255, .03);
            transition: all .2s
        }

        .cell.win {
            background: rgba(227, 30, 36, .15);
            transform: scale(1.08)
        }

        .cell.scatter {
            background: rgba(227, 30, 36, .2);
            animation: sc-p .5s infinite
        }

        .cell.bomb {
            background: rgba(255, 61, 0, .2);
            animation: bm-s .3s infinite
        }

        @keyframes sc-p {

            0%,
            100% {
                transform: scale(1)
            }

            50% {
                transform: scale(1.12)
            }
        }

        @keyframes bm-s {

            0%,
            100% {
                transform: rotate(0)
            }

            25% {
                transform: rotate(-2deg)
            }

            75% {
                transform: rotate(2deg)
            }
        }

        .game-result {
            text-align: center;
            height: 32px;
            font-weight: 800;
            font-size: 16px;
            padding: 6px 0;
            display: flex;
            align-items: center;
            justify-content: center
        }

        .game-result .win-text {
            color: var(--green);
            display: flex;
            align-items: center;
            gap: 4px
        }

        .game-result .lose-text {
            color: var(--dim)
        }

        .free-spin-badge {
            text-align: center;
            padding: 2px;
            font-size: 11px;
            color: var(--red);
            font-weight: 700
        }

        /* Controls — Stitch-style layout */
        .game-controls {
            display: flex;
            gap: 10px;
            align-items: center;
            justify-content: center;
            padding: 8px 10px 4px
        }

        .ctrl-side-btn {
            width: 56px;
            height: 56px;
            border-radius: var(--radius);
            border: none;
            background: var(--surface2);
            color: var(--dim);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 2px;
            cursor: pointer;
            font-family: 'Montserrat', sans-serif;
            font-size: 9px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: .5px;
            transition: all .15s
        }

        .ctrl-side-btn:active {
            transform: scale(.93);
            background: var(--surface3)
        }

        .ctrl-side-btn .material-symbols-outlined {
            font-size: 20px
        }

        .spin-btn {
            width: 90px;
            height: 70px;
            border-radius: var(--radius);
            border: none;
            font-family: 'Montserrat', sans-serif;
            font-weight: 900;
            cursor: pointer;
            font-size: 11px;
            transition: all .2s;
            text-transform: uppercase;
            letter-spacing: .5px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 2px;
            position: relative
        }

        .spin-btn .material-symbols-outlined {
            font-size: 28px
        }

        .spin-btn.m-spin {
            background: var(--red);
            color: #fff;
            box-shadow: 0 4px 20px var(--red-glow)
        }

        .spin-btn.m-deposit {
            background: var(--green);
            color: #fff;
            animation: glow-g 1.5s infinite
        }

        .spin-btn.m-load {
            background: var(--surface);
            color: var(--dim)
        }

        @keyframes glow-g {

            0%,
            100% {
                box-shadow: 0 0 8px rgba(34, 197, 94, .3)
            }

            50% {
                box-shadow: 0 0 20px rgba(34, 197, 94, .5)
            }
        }

        .spin-btn:disabled {
            opacity: .4;
            cursor: not-allowed
        }

        .spin-btn:active:not(:disabled) {
            transform: scale(.93)
        }

        /* Bet amount strip — [−] ——— 5.0 coins ——— [+] */
        .bet-strip {
            display: flex;
            align-items: center;
            margin: 4px 10px 0;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            height: 48px;
            overflow: hidden
        }

        .bet-strip-btn {
            width: 54px;
            height: 100%;
            border: none;
            background: transparent;
            color: var(--dim);
            font-size: 22px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all .12s;
            font-family: 'Inter', sans-serif;
            flex-shrink: 0
        }

        .bet-strip-btn:active {
            background: rgba(255, 255, 255, .05);
            color: #fff
        }

        .bet-strip-val {
            flex: 1;
            text-align: center;
            font-family: 'Montserrat', sans-serif;
            font-weight: 800;
            font-size: 16px;
            color: #fff;
            letter-spacing: .3px;
            user-select: none
        }

        .bet-strip-val .bet-unit {
            color: var(--red);
            font-size: 12px;
            font-weight: 700;
            margin-left: 4px;
            text-transform: uppercase
        }

        .bet-strip-label {
            display: block;
            font-size: 9px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--dim2);
            text-align: center;
            margin-top: 2px;
            padding: 0 10px
        }

        /* Buy bonus */
        .buy-bonus {
            width: calc(100% - 20px);
            margin: 6px 10px 0;
            padding: 12px 14px;
            border-radius: var(--radius);
            border: 1.5px solid rgba(227, 30, 36, .2);
            background: transparent;
            color: #fff;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            font-family: 'Inter', sans-serif;
            font-size: 13px;
            transition: all .15s
        }

        .buy-bonus:active {
            transform: scale(.97);
            background: rgba(227, 30, 36, .05)
        }

        .bb-left {
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 6px
        }

        .bb-right {
            font-weight: 800;
            color: var(--red)
        }

        /* Speed row (hidden inside AUTO now, but keep for turbo toggle) */
        .speed-row {
            display: none
        }

        /* ======================== */
        /* === BONUSES SCREEN === */
        /* ======================== */
        .bonus-featured {
            margin: 0 16px 16px;
            border-radius: var(--radius-xl);
            background: linear-gradient(180deg, rgba(227, 30, 36, .08), var(--surface) 60%);
            border: 1.5px solid rgba(227, 30, 36, .25);
            overflow: hidden;
            min-height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            position: relative;
            box-shadow: 0 0 16px rgba(227, 30, 36, .08)
        }

        .bonus-featured-content {
            padding: 20px;
            position: relative;
            z-index: 1
        }

        .bonus-featured .bf-tags {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 8px
        }

        .bf-tag {
            font-size: 9px;
            font-weight: 800;
            text-transform: uppercase;
            padding: 3px 8px;
            border-radius: 4px;
            letter-spacing: 1px;
            background: rgba(227, 30, 36, .15);
            color: var(--red);
            border: 1px solid rgba(227, 30, 36, .2)
        }

        .bf-timer {
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 10px;
            color: var(--dim);
            font-weight: 500
        }

        .bf-timer .material-symbols-outlined {
            font-size: 12px
        }

        .bf-title {
            font-family: 'Montserrat', sans-serif;
            font-size: 24px;
            font-weight: 900;
            color: #fff;
            margin-bottom: 4px;
            letter-spacing: -.3px
        }

        .bf-desc {
            font-size: 12px;
            color: var(--dim);
            line-height: 1.5;
            margin-bottom: 16px
        }

        .bf-bottom {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 12px;
            border-top: 1px solid rgba(255, 255, 255, .06)
        }

        .bf-wager-label {
            font-size: 9px;
            text-transform: uppercase;
            font-weight: 800;
            color: var(--dim2);
            letter-spacing: 1px
        }

        .bf-wager-val {
            font-weight: 800;
            color: #fff;
            font-size: 14px
        }

        .bf-activate {
            height: 38px;
            padding: 0 20px;
            border-radius: 20px;
            border: none;
            background: var(--red);
            color: #fff;
            font-family: 'Montserrat', sans-serif;
            font-weight: 700;
            font-size: 12px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            box-shadow: 0 2px 12px var(--red-glow);
            transition: all .15s;
            text-transform: uppercase
        }

        .bf-activate:active {
            transform: scale(.95)
        }

        .bf-activate .material-symbols-outlined {
            font-size: 16px
        }

        /* Bonus list card */
        .bonus-card {
            margin: 0 16px 12px;
            border-radius: var(--radius-lg);
            background: var(--surface);
            border: 1px solid var(--border);
            overflow: hidden;
            display: flex;
            transition: border-color .2s
        }

        .bonus-card:active {
            border-color: rgba(227, 30, 36, .3)
        }

        .bonus-card-img {
            width: 33%;
            min-height: 110px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 36px;
            position: relative
        }

        .bonus-card-img::after {
            content: '';
            position: absolute;
            right: 0;
            top: 0;
            bottom: 0;
            width: 30px;
            background: linear-gradient(90deg, transparent, var(--surface))
        }

        .bonus-card-body {
            flex: 1;
            padding: 14px 14px 14px 8px;
            display: flex;
            flex-direction: column;
            justify-content: center
        }

        .bonus-card-title {
            font-family: 'Montserrat', sans-serif;
            font-size: 15px;
            font-weight: 800;
            color: #fff;
            margin-bottom: 4px
        }

        .bonus-card-desc {
            font-size: 11px;
            color: var(--dim);
            line-height: 1.4;
            margin-bottom: 10px
        }

        .bonus-card-btn {
            height: 32px;
            padding: 0 16px;
            border-radius: 16px;
            border: 1.5px solid var(--red);
            background: transparent;
            color: var(--red);
            font-family: 'Montserrat', sans-serif;
            font-weight: 700;
            font-size: 11px;
            cursor: pointer;
            transition: all .15s;
            text-transform: uppercase;
            align-self: flex-start
        }

        .bonus-card-btn:active {
            background: rgba(227, 30, 36, .08)
        }

        /* Locked bonus */
        .bonus-locked {
            margin: 0 16px 12px;
            border-radius: var(--radius-lg);
            background: var(--surface);
            border: 1px solid var(--border);
            overflow: hidden;
            display: flex;
            opacity: .5
        }

        .bonus-locked .lock-icon {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(0, 0, 0, .6);
            border-radius: 50%;
            width: 28px;
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: center
        }

        /* Bonus Segments */
        .bonus-seg {
            background: transparent;
            color: var(--dim)
        }

        .bonus-seg.active {
            background: var(--surface2);
            color: #fff;
            border: 1px solid rgba(255, 255, 255, .08) !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, .3)
        }

        /* Glass Bonus Card */
        .glass-card {
            background: linear-gradient(135deg, var(--surface) 0%, var(--surface2) 100%);
            border: 1px solid rgba(227, 30, 36, .3);
            border-radius: 14px;
            padding: 20px;
            position: relative;
            overflow: hidden
        }

        .glass-card .gc-bg-icon {
            position: absolute;
            top: 0;
            right: 0;
            padding: 16px;
            opacity: .07
        }

        .glass-card .gc-bg-icon .material-symbols-outlined {
            font-size: 56px;
            color: var(--red)
        }

        .gc-title {
            font-family: 'Montserrat', sans-serif;
            font-size: 18px;
            font-weight: 800;
            color: #fff;
            margin-bottom: 4px;
            position: relative;
            z-index: 1
        }

        .gc-desc {
            font-size: 12px;
            color: var(--dim);
            line-height: 1.4;
            margin-bottom: 14px;
            position: relative;
            z-index: 1
        }

        .gc-progress {
            margin-bottom: 16px;
            position: relative;
            z-index: 1
        }

        .gc-progress-header {
            display: flex;
            justify-content: space-between;
            font-size: 10px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: .8px;
            margin-bottom: 6px
        }

        .gc-progress-header .label {
            color: var(--red)
        }

        .gc-progress-header .val {
            color: #fff
        }

        .gc-progress-bar {
            width: 100%;
            height: 5px;
            background: rgba(227, 30, 36, .15);
            border-radius: 3px;
            overflow: hidden
        }

        .gc-progress-fill {
            height: 100%;
            background: var(--red);
            border-radius: 3px;
            transition: width .5s
        }

        .gc-btn-primary {
            width: 100%;
            height: 42px;
            border: none;
            border-radius: 8px;
            background: var(--red);
            color: #fff;
            font-family: 'Montserrat', sans-serif;
            font-weight: 800;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            cursor: pointer;
            transition: all .15s;
            position: relative;
            z-index: 1
        }

        .gc-btn-primary:active {
            transform: scale(.97);
            opacity: .9
        }

        .gc-btn-outline {
            width: 100%;
            height: 42px;
            border: 1.5px solid rgba(227, 30, 36, .4);
            border-radius: 8px;
            background: rgba(227, 30, 36, .06);
            color: var(--red);
            font-family: 'Montserrat', sans-serif;
            font-weight: 800;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            cursor: pointer;
            transition: all .15s;
            position: relative;
            z-index: 1
        }

        .gc-btn-outline:active {
            transform: scale(.97);
            background: rgba(227, 30, 36, .12)
        }

        .gc-timer {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 12px;
            background: rgba(0, 0, 0, .3);
            border: 1px solid var(--border);
            border-radius: 8px;
            margin-bottom: 16px;
            position: relative;
            z-index: 1
        }

        .gc-timer .material-symbols-outlined {
            color: var(--red);
            font-size: 20px
        }

        .gc-timer-label {
            font-size: 9px;
            text-transform: uppercase;
            font-weight: 800;
            color: var(--dim2);
            letter-spacing: 1px;
            line-height: 1
        }

        .gc-timer-val {
            font-size: 12px;
            font-weight: 800;
            color: #fff;
            text-transform: uppercase;
            letter-spacing: 2px
        }

        .gc-vip-tag {
            padding: 3px 8px;
            font-size: 9px;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: .5px;
            background: rgba(227, 30, 36, .15);
            color: var(--red);
            border: 1px solid rgba(227, 30, 36, .25);
            border-radius: 4px
        }

        /* History Item */
        .history-item {
            background: rgba(255, 255, 255, .03);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 14px;
            transition: all .15s
        }

        .history-item.expired {
            opacity: .6
        }

        .hi-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px
        }

        .hi-icon {
            width: 40px;
            height: 40px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0
        }

        .hi-icon.active {
            background: rgba(227, 30, 36, .08);
            border: 1px solid rgba(227, 30, 36, .15)
        }

        .hi-icon.inactive {
            background: var(--surface2);
            border: 1px solid var(--border)
        }

        .hi-info {
            flex: 1;
            margin-left: 10px
        }

        .hi-title {
            font-family: 'Montserrat', sans-serif;
            font-size: 13px;
            font-weight: 800;
            color: #fff;
            letter-spacing: .3px
        }

        .hi-date {
            font-size: 10px;
            color: var(--dim2);
            margin-top: 2px
        }

        .hi-amount {
            text-align: right
        }

        .hi-val {
            font-size: 13px;
            font-weight: 800;
            color: #fff
        }

        .hi-val-label {
            font-size: 9px;
            font-weight: 800;
            text-transform: uppercase;
            color: var(--dim2)
        }

        .hi-bottom {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-top: 10px;
            border-top: 1px solid var(--border)
        }

        .hi-status {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 11px;
            font-weight: 600;
            color: var(--dim)
        }

        .hi-status .material-symbols-outlined {
            font-size: 16px
        }

        .hi-status.completed .material-symbols-outlined {
            color: var(--red)
        }

        .hi-status.completed {
            color: var(--text)
        }

        .hi-badge {
            font-size: 9px;
            font-weight: 800;
            padding: 4px 8px;
            border-radius: 4px;
            background: rgba(255, 255, 255, .04);
            border: 1px solid rgba(255, 255, 255, .08);
            color: var(--dim2);
            text-transform: uppercase;
            letter-spacing: .5px
        }

        .bonus-locked .lock-icon .material-symbols-outlined {
            font-size: 14px;
            color: var(--dim)
        }

        .bonus-locked-body {
            flex: 1;
            padding: 14px;
            position: relative
        }

        .bonus-locked .bl-title {
            font-family: 'Montserrat', sans-serif;
            font-size: 14px;
            font-weight: 800;
            color: var(--dim)
        }

        .bonus-locked .bl-desc {
            font-size: 10px;
            color: var(--dim2);
            margin-bottom: 8px
        }

        .bl-progress {
            height: 4px;
            background: var(--surface2);
            border-radius: 2px;
            overflow: hidden
        }

        .bl-progress-fill {
            height: 100%;
            background: var(--dim);
            border-radius: 2px
        }

        .bl-progress-label {
            font-size: 9px;
            color: var(--dim2);
            text-align: right;
            margin-top: 3px
        }

        /* ======================== */
        /* === WALLET SCREEN === */
        /* ======================== */
        .wallet-balance {
            text-align: center;
            padding: 24px 16px 16px
        }

        .wallet-balance-label {
            font-size: 10px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: var(--dim);
            font-family: 'Montserrat', sans-serif;
            margin-bottom: 4px
        }

        .wallet-balance-amount {
            display: flex;
            align-items: baseline;
            justify-content: center;
            gap: 8px
        }

        .wallet-balance-amount h1 {
            font-family: 'Montserrat', sans-serif;
            font-size: 48px;
            font-weight: 900;
            color: #fff;
            letter-spacing: -2px
        }

        .wallet-balance-amount .unit {
            font-family: 'Montserrat', sans-serif;
            font-size: 22px;
            font-weight: 700;
            color: var(--red)
        }

        .wallet-balance-usd {
            font-size: 13px;
            color: var(--dim);
            margin-top: 2px
        }

        .wallet-actions {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            padding: 0 16px;
            margin-bottom: 16px
        }

        .wallet-actions .btn-primary {
            height: 50px;
            font-size: 13px
        }

        .wallet-actions .btn-outline {
            height: 50px;
            font-size: 13px
        }

        .wallet-history-btn {
            margin: 0 16px 16px;
            height: 44px;
            border-radius: var(--radius);
            border: 1px solid var(--border);
            background: var(--surface);
            color: var(--dim);
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            font-size: 13px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: all .15s;
            width: calc(100% - 32px)
        }

        .wallet-history-btn:active {
            background: var(--surface2)
        }

        .wallet-history-btn .material-symbols-outlined {
            font-size: 18px
        }

        .wallet-assets {
            padding: 0 16px;
            margin-bottom: 16px
        }

        .wallet-assets-label {
            font-size: 10px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--dim);
            font-family: 'Montserrat', sans-serif;
            margin-bottom: 10px
        }

        .asset-row {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px
        }

        .asset-btn {
            height: 42px;
            border-radius: var(--radius);
            border: 1px solid var(--border);
            background: var(--surface);
            color: var(--dim);
            font-family: 'Montserrat', sans-serif;
            font-weight: 600;
            font-size: 13px;
            cursor: pointer;
            transition: all .15s
        }

        .asset-btn.active {
            border: 2px solid var(--red);
            color: #fff;
            background: rgba(227, 30, 36, .06);
            box-shadow: 0 0 8px var(--red-glow)
        }

        /* Deposit info card */
        .deposit-card {
            margin: 0 16px 16px;
            padding: 20px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-xl)
        }

        .deposit-card .dc-network {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(0, 0, 0, .3);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 10px 12px;
            margin-bottom: 16px
        }

        .dc-network-left {
            display: flex;
            align-items: center;
            gap: 8px
        }

        .dc-network .dc-dot {
            width: 8px;
            height: 8px;
            background: var(--red);
            border-radius: 50%;
            box-shadow: 0 0 6px var(--red);
            animation: pulse-dot 2s infinite
        }

        @keyframes pulse-dot {

            0%,
            100% {
                opacity: 1
            }

            50% {
                opacity: .5
            }
        }

        .dc-network .dc-name {
            font-size: 13px;
            font-weight: 600
        }

        .dc-network .dc-status {
            font-size: 9px;
            font-weight: 800;
            text-transform: uppercase;
            color: var(--red);
            letter-spacing: 1px;
            border: 1px solid rgba(227, 30, 36, .2);
            background: rgba(227, 30, 36, .05);
            padding: 2px 8px;
            border-radius: 4px
        }

        .dc-info {
            text-align: center;
            padding: 8px 0;
            font-size: 12px;
            color: var(--dim);
            margin-bottom: 12px
        }

        .dc-info span {
            color: #fff;
            font-weight: 700
        }

        .dc-address-box {
            display: flex;
            align-items: center;
            gap: 6px;
            background: rgba(0, 0, 0, .3);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 6px 6px 6px 14px
        }

        .dc-address {
            flex: 1;
            font-family: monospace;
            font-size: 11px;
            color: var(--dim);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap
        }

        .dc-copy {
            width: 36px;
            height: 36px;
            border-radius: 8px;
            border: none;
            background: var(--surface2);
            color: var(--dim);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all .15s
        }

        .dc-copy:active {
            background: var(--red);
            color: #fff
        }

        .dc-copy .material-symbols-outlined {
            font-size: 16px
        }

        .dc-note {
            display: flex;
            align-items: flex-start;
            gap: 8px;
            background: rgba(227, 30, 36, .04);
            border: 1px solid rgba(227, 30, 36, .12);
            border-radius: var(--radius);
            padding: 12px;
            margin-top: 12px
        }

        .dc-note .material-symbols-outlined {
            font-size: 16px;
            color: var(--red);
            margin-top: 1px;
            flex-shrink: 0
        }

        .dc-note p {
            font-size: 11px;
            color: var(--dim);
            line-height: 1.5
        }

        .dc-note p span {
            color: var(--red);
            font-weight: 700
        }

        /* ======================== */
        /* === REFERRAL SCREEN === */
        /* ======================== */
        .ref-hero {
            margin: 16px;
            border-radius: var(--radius-xl);
            background: var(--surface);
            border: 1px solid var(--border);
            padding: 28px 20px;
            text-align: center;
            position: relative;
            overflow: hidden
        }

        .ref-hero::before {
            content: '';
            position: absolute;
            top: -60px;
            right: -40px;
            width: 180px;
            height: 180px;
            background: radial-gradient(circle, rgba(227, 30, 36, .12), transparent 70%);
            border-radius: 50%
        }

        .ref-hero::after {
            content: '';
            position: absolute;
            bottom: -40px;
            left: -40px;
            width: 150px;
            height: 150px;
            background: radial-gradient(circle, rgba(227, 30, 36, .08), transparent 70%);
            border-radius: 50%
        }

        .ref-hero-icon {
            margin-bottom: 12px;
            position: relative;
            z-index: 1;
            display: flex;
            align-items: center;
            justify-content: center
        }

        .ref-hero h1 {
            font-family: 'Montserrat', sans-serif;
            font-size: 26px;
            font-weight: 900;
            margin-bottom: 6px;
            position: relative;
            z-index: 1;
            letter-spacing: -.5px
        }

        .ref-hero h1 span {
            color: var(--red)
        }

        .ref-hero p {
            font-size: 13px;
            color: var(--dim);
            line-height: 1.5;
            position: relative;
            z-index: 1
        }

        .ref-hero p b {
            color: #fff
        }

        .ref-link-card {
            margin: 0 16px 16px;
            padding: 2px;
            border-radius: var(--radius-lg);
            background: linear-gradient(90deg, rgba(227, 30, 36, .3), var(--red), rgba(227, 30, 36, .3));
            box-shadow: 0 0 12px rgba(227, 30, 36, .15)
        }

        .ref-link-inner {
            background: var(--surface);
            border-radius: calc(var(--radius-lg) - 2px);
            padding: 16px
        }

        .ref-link-label {
            text-align: center;
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--dim);
            margin-bottom: 12px
        }

        .ref-link-box {
            display: flex;
            align-items: center;
            gap: 6px;
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 4px 4px 4px 12px
        }

        .ref-link-box .ref-url {
            flex: 1;
            font-size: 12px;
            font-weight: 500;
            color: var(--dim);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap
        }

        .ref-link-box .ref-copy {
            height: 38px;
            padding: 0 16px;
            border-radius: 8px;
            border: none;
            background: var(--red);
            color: #fff;
            font-family: 'Montserrat', sans-serif;
            font-weight: 700;
            font-size: 12px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all .15s
        }

        .ref-link-box .ref-copy:active {
            transform: scale(.95)
        }

        .ref-link-box .ref-copy .material-symbols-outlined {
            font-size: 16px
        }

        .ref-stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            padding: 0 16px;
            margin-bottom: 16px
        }

        .ref-stat-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            transition: border-color .2s
        }

        .ref-stat-card:hover {
            border-color: rgba(227, 30, 36, .2)
        }

        .ref-stat-top {
            display: flex;
            justify-content: space-between;
            align-items: center
        }

        .ref-stat-icon {
            width: 36px;
            height: 36px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center
        }

        .ref-stat-icon .material-symbols-outlined {
            font-size: 18px
        }

        .ref-stat-icon.people {
            background: rgba(227, 30, 36, .08);
            color: var(--red)
        }

        .ref-stat-icon.money {
            background: rgba(59, 130, 246, .08);
            color: var(--blue)
        }

        .ref-stat-badge {
            font-size: 10px;
            font-weight: 700;
            color: var(--green);
            background: rgba(34, 197, 94, .08);
            padding: 2px 8px;
            border-radius: 10px
        }

        .ref-stat-label {
            font-size: 10px;
            font-weight: 600;
            color: var(--dim)
        }

        .ref-stat-val {
            font-family: 'Montserrat', sans-serif;
            font-size: 24px;
            font-weight: 900;
            color: #fff
        }

        .ref-how {
            margin: 0 16px 16px
        }

        .ref-how-title {
            font-family: 'Montserrat', sans-serif;
            font-size: 15px;
            font-weight: 800;
            margin-bottom: 12px
        }

        .ref-steps {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 20px
        }

        .ref-step {
            display: flex;
            gap: 14px;
            margin-bottom: 20px
        }

        .ref-step:last-child {
            margin-bottom: 0
        }

        .ref-step-line {
            display: flex;
            flex-direction: column;
            align-items: center
        }

        .ref-step-num {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: var(--surface2);
            border: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Montserrat', sans-serif;
            font-size: 12px;
            font-weight: 800;
            color: var(--red);
            flex-shrink: 0
        }

        .ref-step:last-child .ref-step-num {
            background: var(--red);
            color: #fff;
            border: none;
            box-shadow: 0 0 10px var(--red-glow)
        }

        .ref-step-connector {
            width: 1px;
            flex: 1;
            background: var(--border);
            margin: 4px 0
        }

        .ref-step-content h3 {
            font-size: 13px;
            font-weight: 700;
            color: #fff;
            margin-bottom: 2px
        }

        .ref-step-content p {
            font-size: 11px;
            color: var(--dim);
            line-height: 1.5
        }

        .ref-share-btn {
            position: fixed;
            bottom: calc(var(--nav-h) + 16px);
            left: 50%;
            transform: translateX(-50%);
            height: 46px;
            padding: 0 28px;
            border-radius: 23px;
            border: none;
            background: #fff;
            color: var(--red);
            font-family: 'Montserrat', sans-serif;
            font-weight: 800;
            font-size: 13px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, .5);
            z-index: 40;
            transition: all .15s
        }

        .ref-share-btn:active {
            transform: translateX(-50%) scale(.95)
        }

        .ref-share-btn .material-symbols-outlined {
            font-size: 18px
        }

        /* ======================== */
        /* === PROFILE SCREEN === */
        /* ======================== */
        .prof-header {
            text-align: center;
            padding: 24px 16px 16px
        }

        .prof-avatar {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            padding: 3px;
            background: var(--red);
            box-shadow: 0 0 16px var(--red-glow);
            margin: 0 auto 12px;
            display: flex;
            align-items: center;
            justify-content: center
        }

        .prof-avatar-inner {
            width: 100%;
            height: 100%;
            border-radius: 50%;
            background: var(--surface);
            border: 2px solid var(--bg);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            overflow: hidden
        }

        .prof-name {
            font-family: 'Montserrat', sans-serif;
            font-size: 22px;
            font-weight: 700;
            color: #fff;
            margin-bottom: 4px;
            letter-spacing: -.3px
        }

        .prof-meta {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            margin-bottom: 16px
        }

        .prof-id {
            font-size: 11px;
            color: var(--dim);
            font-family: monospace;
            letter-spacing: .5px
        }

        .prof-vip-badge {
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 11px;
            color: var(--red);
            font-weight: 700
        }

        .prof-vip-badge .material-symbols-outlined {
            font-size: 14px
        }

        .prof-level {
            padding: 0 16px;
            margin-bottom: 20px
        }

        .prof-level-top {
            display: flex;
            justify-content: space-between;
            margin-bottom: 6px
        }

        .prof-level-name {
            font-size: 10px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--dim);
            font-family: 'Montserrat', sans-serif
        }

        .prof-level-val {
            font-size: 11px;
            font-weight: 600;
            color: var(--red)
        }

        .prof-level .vip-bar {
            margin-bottom: 4px
        }

        .prof-level-xp {
            display: flex;
            justify-content: space-between;
            font-size: 9px;
            color: var(--dim2)
        }

        .prof-stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0;
            margin: 0 16px 16px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            overflow: hidden
        }

        .prof-stat {
            padding: 14px;
            text-align: center;
            border-right: 1px solid var(--border)
        }

        .prof-stat:last-child {
            border-right: none
        }

        .prof-stat-label {
            font-size: 9px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--dim);
            margin-bottom: 4px
        }

        .prof-stat-val {
            font-family: 'Montserrat', sans-serif;
            font-size: 18px;
            font-weight: 800;
            color: #fff
        }

        .prof-referral-btn {
            margin: 0 16px 12px;
            padding: 14px 16px;
            background: var(--surface);
            border: 1.5px solid rgba(227, 30, 36, .25);
            border-radius: var(--radius-lg);
            display: flex;
            align-items: center;
            justify-content: space-between;
            cursor: pointer;
            transition: all .15s;
            box-shadow: 0 0 8px rgba(227, 30, 36, .05)
        }

        .prof-referral-btn:active {
            background: rgba(227, 30, 36, .04)
        }

        .prof-ref-left {
            display: flex;
            align-items: center;
            gap: 12px
        }

        .prof-ref-icon {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: rgba(227, 30, 36, .08);
            border: 1px solid rgba(227, 30, 36, .15);
            display: flex;
            align-items: center;
            justify-content: center
        }

        .prof-ref-icon .material-symbols-outlined {
            font-size: 18px;
            color: var(--red)
        }

        .prof-ref-text h3 {
            font-size: 13px;
            font-weight: 700;
            color: #fff
        }

        .prof-ref-text p {
            font-size: 10px;
            color: var(--dim)
        }

        .prof-referral-btn .material-symbols-outlined {
            color: var(--red);
            font-size: 18px;
            transition: transform .15s
        }

        .prof-referral-btn:active .material-symbols-outlined:last-child {
            transform: translateX(2px)
        }

        .prof-menu {
            margin: 0 16px 16px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            overflow: hidden
        }

        .prof-menu-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 14px 16px;
            border-bottom: 1px solid var(--border);
            cursor: pointer;
            transition: background .15s
        }

        .prof-menu-item:last-child {
            border-bottom: none
        }

        .prof-menu-item:active {
            background: var(--surface2)
        }

        .prof-menu-left {
            display: flex;
            align-items: center;
            gap: 12px
        }

        .prof-menu-left .material-symbols-outlined {
            font-size: 20px;
            color: var(--red)
        }

        .prof-menu-left span:last-child {
            font-size: 13px;
            font-weight: 500
        }

        .prof-menu-item .material-symbols-outlined:last-child {
            font-size: 18px;
            color: var(--dim2)
        }

        .prof-signout {
            display: block;
            margin: 0 auto;
            padding: 12px 24px;
            border: none;
            background: none;
            color: var(--dim);
            font-family: 'Montserrat', sans-serif;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 2px;
            cursor: pointer;
            transition: color .15s
        }

        .prof-signout:active {
            color: var(--red)
        }

        /* ======================== */
        /* === OVERLAYS === */
        /* ======================== */
        .bonus-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, .92);
            z-index: 200;
            display: none;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 12px;
            padding: 20px
        }

        .bonus-overlay.show {
            display: flex
        }

        .bo-title {
            font-family: 'Montserrat', sans-serif;
            font-size: 22px;
            font-weight: 900;
            color: var(--red);
            text-shadow: 0 0 20px var(--red-glow);
            animation: bo-pop .5s ease-out
        }

        @keyframes bo-pop {
            0% {
                transform: scale(0)
            }

            60% {
                transform: scale(1.2)
            }

            100% {
                transform: scale(1)
            }
        }

        .bo-info {
            display: flex;
            gap: 16px
        }

        .bo-info-item {
            text-align: center;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 8px 16px
        }

        .bo-info-item .label {
            font-size: 10px;
            color: var(--dim)
        }

        .bo-info-item .val {
            font-family: 'Montserrat', sans-serif;
            font-size: 18px;
            font-weight: 900;
            color: var(--gold)
        }

        .bo-grid-wrap {
            width: 100%;
            max-width: 380px;
            background: rgba(0, 0, 0, .5);
            border: 2px solid var(--red);
            border-radius: var(--radius-lg);
            padding: 6px
        }

        .bo-grid {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 3px
        }

        .bo-result {
            font-weight: 800;
            font-size: 18px;
            color: var(--green);
            text-align: center;
            min-height: 24px
        }

        .bo-total {
            font-family: 'Montserrat', sans-serif;
            font-size: 28px;
            font-weight: 900;
            color: var(--gold);
            text-align: center
        }

        .bo-close {
            padding: 12px 36px;
            border-radius: var(--radius);
            border: none;
            background: var(--red);
            color: #fff;
            font-family: 'Montserrat', sans-serif;
            font-weight: 900;
            font-size: 15px;
            cursor: pointer;
            display: none;
            box-shadow: 0 4px 16px var(--red-glow)
        }

        /* Wheel overlay */
        .wheel-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, .92);
            z-index: 200;
            display: none;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 20px;
            padding: 20px
        }

        .wheel-overlay.show {
            display: flex
        }

        .wo-title {
            font-family: 'Montserrat', sans-serif;
            font-size: 20px;
            font-weight: 900;
            color: var(--green)
        }

        .wheel-container {
            position: relative;
            width: 260px;
            height: 260px;
            margin: 0 auto
        }

        .wheel-canvas {
            width: 260px;
            height: 260px;
            border-radius: 50%;
            transition: transform 4s cubic-bezier(.17, .67, .05, .99)
        }

        .wheel-pointer {
            position: absolute;
            top: -8px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 28px;
            z-index: 10;
            filter: drop-shadow(0 2px 4px rgba(0, 0, 0, .5))
        }

        .wheel-center {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 44px;
            height: 44px;
            border-radius: 50%;
            background: var(--red);
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Montserrat', sans-serif;
            font-weight: 900;
            font-size: 14px;
            color: #fff;
            box-shadow: 0 0 20px var(--red-glow);
            z-index: 5
        }

        .wo-prize {
            font-family: 'Montserrat', sans-serif;
            font-size: 28px;
            font-weight: 900;
            color: var(--red);
            min-height: 40px
        }

        .wo-btn {
            padding: 14px 40px;
            border-radius: var(--radius);
            border: none;
            background: var(--green);
            color: #fff;
            font-family: 'Montserrat', sans-serif;
            font-weight: 900;
            font-size: 16px;
            cursor: pointer
        }

        /* Toast */
        .toast {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(0);
            background: var(--surface);
            border: 1.5px solid var(--red);
            border-radius: var(--radius-xl);
            padding: 24px 28px;
            text-align: center;
            z-index: 500;
            transition: transform .25s cubic-bezier(.34, 1.56, .64, 1);
            max-width: 300px;
            width: 85%
        }

        .toast.show {
            transform: translate(-50%, -50%) scale(1)
        }

        .toast-icon {
            font-size: 40px;
            margin-bottom: 8px
        }

        .toast-text {
            font-size: 14px;
            font-weight: 700;
            margin-bottom: 14px;
            line-height: 1.4
        }

        .toast-btns {
            display: flex;
            gap: 8px
        }

        .toast-btn {
            flex: 1;
            padding: 10px;
            border-radius: var(--radius);
            border: none;
            font-family: 'Montserrat', sans-serif;
            font-weight: 800;
            font-size: 13px;
            cursor: pointer;
            transition: transform .1s
        }

        .toast-btn:active {
            transform: scale(.95)
        }

        .toast-btn.primary {
            background: var(--red);
            color: #fff;
            box-shadow: 0 2px 10px var(--red-glow)
        }

        .toast-btn.secondary {
            background: var(--surface2);
            color: var(--dim)
        }

        .bomb-pop {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-weight: 900;
            font-size: 44px;
            color: var(--red);
            z-index: 300;
            pointer-events: none;
            animation: bp .7s ease-out forwards
        }

        @keyframes bp {
            0% {
                transform: translate(-50%, -50%) scale(0);
                opacity: 1
            }

            50% {
                transform: translate(-50%, -50%) scale(1.4);
                opacity: 1
            }

            100% {
                transform: translate(-50%, -60%) scale(1);
                opacity: 0
            }
        }

        /* === CRASH GAME === */
        #scrCrash {
            display: none;
            opacity: 0;
            flex-direction: column;
            height: 100vh;
            overflow: hidden;
            background: var(--bg);
            transition: opacity 0.15s ease;
        }

        #scrCrash.active {
            display: flex;
            opacity: 1;
        }

        .crash-graph-container {
            flex: 1;
            position: relative;
            background: radial-gradient(circle at center, rgba(34, 197, 94, 0.1), transparent);
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }

        .crash-canvas {
            width: 100%;
            height: 100%;
            position: absolute;
            inset: 0;
            z-index: 1;
        }

        .crash-value-display {
            position: relative;
            z-index: 2;
            text-align: center;
        }

        .crash-mult {
            font-family: 'Montserrat', sans-serif;
            font-size: 56px;
            font-weight: 900;
            color: #fff;
            text-shadow: 0 0 20px rgba(255, 255, 255, 0.2);
            line-height: 1;
        }

        .crash-mult.crashed {
            color: var(--red);
            text-shadow: 0 0 20px var(--red-glow);
        }

        .crash-mult.active {
            color: var(--green);
            text-shadow: 0 0 20px rgba(34, 197, 94, 0.4);
        }

        .crash-profit {
            font-size: 16px;
            color: var(--green);
            font-weight: 700;
            margin-top: 8px;
            opacity: 0;
            transition: opacity 0.2s;
        }

        .crash-profit.show {
            opacity: 1;
        }

        .crash-history {
            height: 36px;
            background: var(--surface);
            display: flex;
            align-items: center;
            padding: 0 16px;
            gap: 8px;
            overflow-x: auto;
            border-bottom: 1px solid var(--border);
        }

        .crash-history::-webkit-scrollbar {
            display: none;
        }

        .ch-pill {
            padding: 4px 10px;
            border-radius: 12px;
            background: var(--surface2);
            font-size: 11px;
            font-weight: 700;
            white-space: nowrap;
        }

        .ch-pill.high {
            color: var(--green);
            background: rgba(34, 197, 94, 0.1);
        }

        .ch-pill.low {
            color: var(--red);
            background: rgba(227, 30, 36, 0.1);
        }

        .crash-controls {
            padding: 16px;
            background: var(--surface);
            padding-bottom: calc(env(safe-area-inset-bottom) + 16px);
        }

        .crash-bet-inputs {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 16px;
        }

        .cb-box {
            background: var(--surface2);
            border-radius: var(--radius);
            padding: 12px;
            border: 1px solid var(--border);
        }

        .cb-label {
            font-size: 10px;
            color: var(--dim);
            text-transform: uppercase;
            font-weight: 700;
            margin-bottom: 6px;
        }

        .cb-input-row {
            display: flex;
            align-items: center;
        }

        .cb-input {
            flex: 1;
            background: transparent;
            border: none;
            color: #fff;
            font-family: 'Montserrat', sans-serif;
            font-weight: 800;
            font-size: 16px;
            width: 100%;
            outline: none;
        }

        .cb-btn {
            background: var(--surface3);
            color: var(--text);
            border: none;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 700;
            margin-left: 4px;
            cursor: pointer;
        }

        .crash-action-btn {
            width: 100%;
            height: 56px;
            border-radius: var(--radius-lg);
            border: none;
            font-family: 'Montserrat', sans-serif;
            font-size: 18px;
            font-weight: 900;
            color: #fff;
            text-transform: uppercase;
            cursor: pointer;
            transition: all 0.15s;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            line-height: 1.2;
        }

        .crash-action-btn.bet {
            background: var(--green);
            box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3);
        }

        .crash-action-btn.cashout {
            background: var(--gold);
            color: #000;
            box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
        }

        .crash-action-btn.wait {
            background: var(--surface3);
            color: var(--dim);
            pointer-events: none;
        }

        .crash-action-btn.cancel {
            background: var(--red);
            box-shadow: 0 4px 15px rgba(227, 30, 36, 0.3);
        }

        .crash-action-sub {
            font-size: 11px;
            font-weight: 600;
            opacity: 0.8;
            font-family: 'Inter', sans-serif;
        }
    </style>
</head>

<body>

    <!-- ===== HEADER (shared) ===== -->
    <div class="header" id="mainHeader">
        <div class="logo">
            <div class="logo-icon"><span class="material-symbols-outlined">diamond</span></div>
            <div class="logo-text">RUBY<span>BET</span></div>
        </div>
        <div class="header-right">
            <div class="header-bal" onclick="openBalancePopup()" style="display:flex;align-items:center;gap:6px">
                <div id="headerBalCrypto"
                    style="display:flex;align-items:center;gap:3px;padding:4px 8px;border-radius:8px;cursor:pointer;transition:all .15s"
                    class="bal-active">
                    <span style="font-size:12px">💵</span>
                    <span id="headerBal" style="font-weight:800;font-size:13px">...</span>
                </div>
                <div style="width:1px;height:16px;background:var(--border)"></div>
                <div id="headerBalStars"
                    style="display:flex;align-items:center;gap:3px;padding:4px 8px;border-radius:8px;cursor:pointer;transition:all .15s">
                    <span style="font-size:12px">⭐</span>
                    <span id="headerBalStarsVal" style="font-weight:800;font-size:13px">0</span>
                </div>
            </div>
            <div class="header-notif"><span class="material-symbols-outlined">notifications</span>
                <div class="dot"></div>
            </div>
        </div>
    </div>

    <!-- Balance / Currency Popup -->
    <div id="balPopup" style="display:none;position:fixed;top:0;left:0;right:0;bottom:0;z-index:200">
        <div id="balPopupBg" style="position:absolute;inset:0;background:rgba(0,0,0,.5);backdrop-filter:blur(4px)"
            onclick="closeBalancePopup()"></div>
        <div id="balPopupCard"
            style="position:absolute;top:var(--header-h);right:12px;width:300px;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-xl);padding:16px;box-shadow:0 16px 48px rgba(0,0,0,.6);transform:translateY(-8px) scale(.95);opacity:0;transition:all .2s cubic-bezier(.34,1.56,.64,1)">

            <!-- Both balances side by side -->
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px">
                <div onclick="switchActiveWallet('usdt');closeBalancePopup()"
                    style="padding:12px;background:rgba(34,197,94,.05);border:1.5px solid rgba(34,197,94,.2);border-radius:var(--radius);cursor:pointer;text-align:center;transition:all .15s"
                    id="bpUsdtCard">
                    <div style="font-size:20px;margin-bottom:4px">💵</div>
                    <div
                        style="font-size:9px;font-weight:800;text-transform:uppercase;letter-spacing:1px;color:var(--dim);margin-bottom:2px">
                        CRYPTO</div>
                    <div style="font-family:'Montserrat',sans-serif;font-size:18px;font-weight:900;color:#fff"
                        id="bpUsdtVal">$0.00</div>
                </div>
                <div onclick="switchActiveWallet('stars');closeBalancePopup()"
                    style="padding:12px;background:rgba(255,215,0,.03);border:1.5px solid rgba(255,215,0,.15);border-radius:var(--radius);cursor:pointer;text-align:center;transition:all .15s"
                    id="bpStarsCard">
                    <div style="font-size:20px;margin-bottom:4px">⭐</div>
                    <div
                        style="font-size:9px;font-weight:800;text-transform:uppercase;letter-spacing:1px;color:var(--dim);margin-bottom:2px">
                        STARS</div>
                    <div style="font-family:'Montserrat',sans-serif;font-size:18px;font-weight:900;color:#FFD700"
                        id="bpStarsVal">0</div>
                </div>
            </div>

            <!-- Crypto Bonus badge -->
            <div
                style="display:flex;align-items:center;gap:8px;padding:8px 12px;background:rgba(34,197,94,.06);border:1px solid rgba(34,197,94,.15);border-radius:var(--radius);margin-bottom:12px">
                <span style="font-size:16px">🔥</span>
                <div style="flex:1">
                    <div style="font-size:11px;font-weight:700;color:var(--green)">+7% Crypto Bonus</div>
                    <div style="font-size:9px;color:var(--dim)">On every CryptoBot deposit</div>
                </div>
                <div
                    style="font-size:9px;font-weight:800;color:var(--dim);background:var(--surface2);padding:2px 6px;border-radius:4px">
                    x3 WAGER</div>
            </div>

            <!-- Currency selector (USDT mode) -->
            <div id="bpCurrencies" style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-bottom:12px">
                <button class="pill" data-cur="USD" onclick="setCurrencyPopup('USD')"
                    style="justify-content:center;height:30px;font-size:10px">$ USD</button>
                <button class="pill" data-cur="EUR" onclick="setCurrencyPopup('EUR')"
                    style="justify-content:center;height:30px;font-size:10px">€ EUR</button>
                <button class="pill" data-cur="UAH" onclick="setCurrencyPopup('UAH')"
                    style="justify-content:center;height:30px;font-size:10px">₴ UAH</button>
            </div>

            <!-- Quick actions -->
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
                <button class="btn-primary" onclick="closeBalancePopup();nav('wallet')"
                    style="height:38px;font-size:11px;border-radius:10px">
                    <span class="material-symbols-outlined" style="font-size:14px">arrow_downward</span> DEPOSIT
                </button>
                <button class="btn-outline"
                    onclick="closeBalancePopup();nav('wallet');setTimeout(function(){switchCashierTab('withdraw')},100)"
                    style="height:38px;font-size:11px;border-radius:10px;color:var(--dim)">
                    <span class="material-symbols-outlined" style="font-size:14px">arrow_upward</span> WITHDRAW
                </button>
            </div>
        </div>
    </div>

    <!-- ===== SEARCH OVERLAY ===== -->
    <div class="search-overlay" id="searchOverlay">
        <div class="search-header">
            <button onclick="closeSearch()"
                style="background:none;border:none;color:var(--dim);cursor:pointer;padding:4px"><span
                    class="material-symbols-outlined">arrow_back</span></button>
            <input type="text" class="search-input" id="searchInput" placeholder="Search games..."
                oninput="onSearchInput(this.value)">
            <button onclick="document.getElementById('searchInput').value='';onSearchInput('')"
                style="background:none;border:none;color:var(--dim);cursor:pointer;padding:4px"><span
                    class="material-symbols-outlined">close</span></button>
        </div>
        <div class="search-results" id="searchResults">
            <div class="search-empty"><span class="material-symbols-outlined"
                    style="font-size:48px;display:block;margin-bottom:8px">search</span>Type to search games</div>
        </div>
    </div>

    <!-- ===== SCREEN: LOBBY ===== -->
    <div class="screen active" id="scrLobby">
        <div class="lobby-search" onclick="openSearch()"><span class="material-symbols-outlined">search</span><span
                id="searchPlaceholder">Search games...</span></div>

        <div class="hero-banner">
            <div class="hero-tag"><span class="material-symbols-outlined">local_fire_department</span><span
                    id="heroTag">HOT</span></div>
            <h2 class="hero-title" id="heroTitle">RUBY <span>JACKPOT</span></h2>
            <p class="hero-sub" id="heroSub">5,000 coins prize pool</p>
            <button class="hero-btn" onclick="nav('game')"><span class="material-symbols-outlined">play_arrow</span>
                <span id="heroPlay">PLAY NOW</span></button>
        </div>

        <div class="wheel-banner" id="wheelBanner" onclick="openWheel()"
            style="display:flex;align-items:center;justify-content:space-between">
            <div style="display:flex;align-items:center;gap:12px">
                <div class="wheel-icon">🎡</div>
                <div class="wheel-info">
                    <h3
                        style="font-family:'Montserrat',sans-serif;font-size:14px;font-weight:800;text-transform:uppercase;letter-spacing:.5px;margin:0">
                        DAILY BONUS WHEEL</h3>
                    <p id="wheelSub" style="font-size:11px;color:var(--dim);margin:2px 0 0">Spin for free every 24h</p>
                </div>
            </div>
            <div
                style="background:var(--red);color:#fff;padding:8px 16px;border-radius:20px;font-family:'Montserrat',sans-serif;font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:1px;box-shadow:0 2px 8px rgba(227,30,36,.4);cursor:pointer">
                SPIN</div>
        </div>

        <!-- Live Drops Ticker -->
        <div class="live-drops-section">
            <div class="live-drops-header">
                <div class="live-drops-dot"></div>
                <div class="live-drops-title">LIVE DROPS</div>
            </div>
            <div class="live-drops-scroll" id="liveDropsScroll"></div>
        </div>

        <div class="vip-strip" id="vipStrip">
            <div class="vip-strip-info">
                <div class="vip-strip-top">
                    <div class="vip-strip-name"><span id="vipIcon">🥉</span> <span id="vipName">Bronze</span></div>
                    <div class="vip-strip-pct" id="vipPct"></div>
                </div>
                <div class="vip-bar">
                    <div class="vip-bar-fill" id="vipBar" style="width:0%"></div>
                </div>
            </div>
        </div>

        <!-- TOP WINNINGS LEADERBOARD -->
        <div class="section">
            <div class="section-head">
                <div class="section-title"><span class="material-symbols-outlined"
                        style="color:#FFD700;font-size:16px;margin-right:4px">emoji_events</span><span
                        id="secTopWins">TOP WINNINGS</span></div>
            </div>
            <div class="top-wins-section">
                <div class="top-wins-tabs">
                    <div class="tw-tab active" onclick="switchTopWins('day',this)" id="twDay">Day</div>
                    <div class="tw-tab" onclick="switchTopWins('week',this)" id="twWeek">Week</div>
                    <div class="tw-tab" onclick="switchTopWins('month',this)" id="twMonth">Month</div>
                    <div class="tw-tab" onclick="switchTopWins('all',this)" id="twAll">All Time</div>
                </div>
                <div id="topWinsList"></div>
            </div>
        </div>

        <div class="section">
            <div class="section-head">
                <div class="section-title" id="secCat">CATEGORIES</div>
                <div class="section-more" id="secCatMore">VIEW ALL</div>
            </div>
            <div class="cat-row" id="catRow"></div>
        </div>

        <!-- GAME PROVIDERS -->
        <div class="section">
            <div class="section-head">
                <div class="section-title"><span class="material-symbols-outlined"
                        style="color:var(--red);font-size:16px;margin-right:4px">sports_esports</span><span
                        id="secProviders">PROVIDERS</span></div>
            </div>
            <div class="providers-row" id="providersRow"></div>
        </div>

        <div class="section" style="margin-bottom:0">
            <div class="section-head">
                <div class="section-title"><span class="material-symbols-outlined"
                        style="color:var(--red);font-size:16px;margin-right:4px">local_fire_department</span><span
                        id="secTrend">TRENDING NOW</span></div>
            </div>
            <div id="gameGrid" class="grid grid-cols-2 gap-[12px] px-[16px] mb-[20px]"></div>
        </div>

        <div style="height:20px"></div>
    </div>

    <!-- ===== SCREEN: CRASH ===== -->
    <div class="screen" id="scrCrash">
        <div class="game-header">
            <div class="game-back" onclick="nav('lobby')"><span class="material-symbols-outlined">arrow_back</span>
            </div>
            <div class="game-title-bar" style="display:flex;align-items:center;gap:6px">CRASH <span class="badge"
                    style="background:rgba(227,30,36,0.1);color:var(--red);border:1px solid var(--red);font-size:9px;padding:2px 6px">PROVABLY
                    FAIR</span></div>
            <div class="game-bal"><span class="material-symbols-outlined">toll</span><span id="crashBal">0.00</span>
            </div>
        </div>

        <div class="crash-history" id="crashHistory">
            <div class="ch-pill low">1.00x</div>
            <div class="ch-pill high">2.45x</div>
            <div class="ch-pill high">10.20x</div>
            <div class="ch-pill low">1.12x</div>
        </div>

        <div class="crash-graph-container">
            <canvas class="crash-canvas" id="crashCanvas"></canvas>
            <div class="crash-value-display">
                <div class="crash-mult" id="crashMult">1.00x</div>
                <div class="crash-profit" id="crashProfit">Profit: +0.00 🪙</div>
            </div>
        </div>

        <div class="crash-controls">
            <div class="crash-bet-inputs">
                <div class="cb-box">
                    <div class="cb-label">BET AMOUNT</div>
                    <div class="cb-input-row">
                        <input type="number" class="cb-input" id="crashBetAmount" value="10.00" step="0.5">
                        <button class="cb-btn"
                            onclick="document.getElementById('crashBetAmount').value=(parseFloat(document.getElementById('crashBetAmount').value)/2).toFixed(2)">1/2</button>
                        <button class="cb-btn"
                            onclick="document.getElementById('crashBetAmount').value=(parseFloat(document.getElementById('crashBetAmount').value)*2).toFixed(2)">2x</button>
                    </div>
                </div>
                <div class="cb-box">
                    <div class="cb-label">AUTO CASHOUT</div>
                    <div class="cb-input-row">
                        <input type="number" class="cb-input" id="crashAutoCashout" value="2.00" step="0.1">
                        <div style="font-family:'Montserrat',sans-serif;font-weight:800;color:var(--dim)">X</div>
                    </div>
                </div>
            </div>

            <button class="crash-action-btn bet" id="crashBtn" onclick="crashAction()">
                BET<br><span class="crash-action-sub">Next Round</span>
            </button>
        </div>
    </div>

    <!-- ===== SCREEN: GAME (Ruby Slots) ===== -->
    <div class="screen" id="scrGame">
        <div class="game-header">
            <div class="game-back" onclick="nav('lobby')"><span class="material-symbols-outlined">arrow_back</span>
            </div>
            <div class="game-title-bar">RUBY SLOTS</div>
            <div class="game-bal"><span class="material-symbols-outlined">toll</span><span id="gameBal">0</span></div>
        </div>
        <div class="jackpot-display">
            <div class="jackpot-label" id="jackpotLabel">GRAND JACKPOT</div>
            <div class="jackpot-amount">50,000<span>coins</span></div>
        </div>
        <div class="grid-frame" id="gridFrame">
            <div class="grid" id="grid"></div>
        </div>
        <div class="game-result" id="gameResult"></div>
        <div class="free-spin-badge" id="freeBadge"></div>
        <div class="game-controls">
            <button class="ctrl-side-btn" onclick="toggleAutoSpeed()"><span
                    class="material-symbols-outlined">sync</span><span id="autoLabel">AUTO</span></button>
            <button class="spin-btn m-load" id="spinBtn" onclick="doSpin()"><span class="material-symbols-outlined"
                    id="spinIcon">play_arrow</span><span id="spinTxt">...</span></button>
            <button class="ctrl-side-btn" onclick="setMaxBet()"><span
                    style="font-family:'Montserrat',sans-serif;font-size:14px;font-weight:900">MAX</span><span>MAX</span></button>
        </div>
        <div class="bet-strip">
            <button class="bet-strip-btn" onclick="changeBet(-1)">−</button>
            <div class="bet-strip-val"><span id="betDisplay">5.0</span><span class="bet-unit" id="betUnit">coins</span>
            </div>
            <button class="bet-strip-btn" onclick="changeBet(1)">+</button>
        </div>
        <div class="bet-strip-label" id="betAmountLabel">BET AMOUNT</div>
        <button class="buy-bonus" onclick="buyBonus()">
            <div class="bb-left">🔥 <span id="bbLabel">Buy Bonus</span></div>
            <div class="bb-right"><span id="bbPrice">500</span> 🪙</div>
        </button>
        <!-- speed is toggled via AUTO button now -->
    </div>

    <!-- ===== SCREEN: BONUSES ===== -->
    <div class="screen" id="scrBonuses">
        <div style="padding:16px 16px 8px">
            <h2 style="font-family:'Montserrat',sans-serif;font-size:22px;font-weight:900" id="bonusTitle">Bonuses</h2>
        </div>
        <div class="pill-row" id="bonusPills"></div>

        <div class="bonus-featured">
            <div
                style="position:absolute;inset:0;background:url('https://lh3.googleusercontent.com/aida-public/AB6AXuAV67NDOkqHDYuJOwD9Je6tBpmvW3RSI4HF0XkpQdgV_iaaVZYQdnLiQU89PymnRn5IxYBRn0BekcKrZ7NHIYjIugI9wO6OBWtjh95WkV_gWTsuQYmVQBUUNzx_4PBG6K0GmTJ0X4UIHtuR-300bhj-NrT24I4jFK3PVoXbEiArjjbMMNC2Z1gegewHMhPAo6Jv8jx7YoLzIBfS7qP7BZW6Egl5S2nvhVfyUlcT7IWmtAyp3Nmk9-kJ1ey0wszCI9yv8Z5gVji0xsQ') center/cover;opacity:.4">
            </div>
            <div
                style="position:absolute;inset:0;background:linear-gradient(to top,#000 0%,rgba(0,0,0,.8) 40%,transparent 100%)">
            </div>
            <div class="bonus-featured-content">
                <div class="bf-tags">
                    <div class="bf-tag" id="bfTag">EXCLUSIVE</div>
                    <div class="bf-timer"><span class="material-symbols-outlined">schedule</span><span
                            id="bfTimer">Expires in 24h</span></div>
                </div>
                <div class="bf-title" id="bfTitle">100% Deposit Match</div>
                <div class="bf-desc" id="bfDesc">Get up to 1 BTC on your first deposit. Double your playing money
                    instantly.</div>
                <div class="bf-bottom">
                    <div>
                        <div class="bf-wager-label" id="bfWagerL">WAGER</div>
                        <div class="bf-wager-val">x30</div>
                    </div>
                    <button class="bf-activate" onclick="nav('wallet')"><span id="bfActivate">Activate</span><span
                            class="material-symbols-outlined">arrow_forward</span></button>
                </div>
            </div>
        </div>

        <div class="bonus-card" id="bonusCard1">
            <div class="bonus-card-img"
                style="background:url('https://lh3.googleusercontent.com/aida-public/AB6AXuCGPEWfXzJNFUB_EXtz51yNIgZjSz3ob9Sd6-OvSGCEov_UGnbjxRwxMthy3MaZd1y3sSKFQxwzinGVFSSUX6MX9LyQcbKOBjS5_h1pMDeP_qC8HgHFFIgVYK41U0IvGrywNBdnYg_6F9KYsRPzmehtL1exPYlIBqyl0I_OSqEwsbDA2rCwRGfu5u_cfHLtbQ7-BRMS0J7mw0JvhGp8lvR9IZ4OtqySVweNv6ohZpAhMhQlsEN84latpHmJh9r7dfdWo9zYOsB4JI0') center/cover">
            </div>
            <div class="bonus-card-body">
                <div class="bonus-card-title" id="bc1Title">50 Free Spins</div>
                <div class="bonus-card-desc" id="bc1Desc">Valid for Ruby Slots. No deposit required for new players.
                </div>
                <button class="bonus-card-btn" id="bc1Btn">Claim Now</button>
            </div>
        </div>

        <div class="bonus-card" id="bonusCard2">
            <div class="bonus-card-img"
                style="background:url('https://lh3.googleusercontent.com/aida-public/AB6AXuDaEolN36F7I9DO5xzDpZJT44gKy0UqcrJkYSpxyvjhw60tyAD7Gy1Bh8-CCjn0wUqGk1dsU3gdG_wlCSodYaiglPb9p8QgUqGUehCxqDwVJx93ersDjvbFa3lgxVwIN2gd29K0ZxblLEP1EkgNZjgTh-fyy3QTKfOvEz8y3gytYBMe2jAJiNryHDsJPpexYxJRkJes_Fb1dmeQ8JqtUOssDqpIUiDNt9FwWXyXoN3at4S1zDC3DhMbXR_TZYjG8VkEpKZFQ2t4ucw') center/cover">
            </div>
            <div class="bonus-card-body">
                <div class="bonus-card-title" id="bc2Title">Weekly Cashback</div>
                <div class="bonus-card-desc" id="bc2Desc">Get 10% back on all losses every Monday. VIP tiers get up to
                    20%.</div>
                <button class="bonus-card-btn" id="bc2Btn">Join Club</button>
            </div>
        </div>

        <div class="bonus-locked" style="position:relative">
            <div
                style="width:33%;min-height:100px;background:url('https://lh3.googleusercontent.com/aida-public/AB6AXuB75EFJ8WIHV-d3TCC0alchWDHTnjGNxWnlJ-CXg6bUaiLzn5to-juivqE1pzeF5TptEeGKwMiKm5NxX5ceNXqUF8x0mTtKAGfHxwEB7-N6TDbNSBxzgVPMLvcPL-WfAIfpJ7o2OL92a__p0S8W_kps90q9TiQ29-7BWlUNCnuZz77-TLZDCiNaUpGKDAs2Tg67FuFyipOljK3xuYXjy0Ak2HIjQODAxVnZH8zc-AO4k8AV6WfqGNcUV0aOMUDJQ77HTwTifyNSP3Y') center/cover;filter:grayscale(1);flex-shrink:0">
            </div>
            <div class="lock-icon"><span class="material-symbols-outlined">lock</span></div>
            <div class="bonus-locked-body">
                <div class="bl-title" id="blTitle">Diamond VIP Status</div>
                <div class="bl-desc" id="blDesc">Unlock exclusive tournaments.</div>
                <div class="bl-progress">
                    <div class="bl-progress-fill" style="width:45%"></div>
                </div>
                <div class="bl-progress-label">Level 4/10</div>
            </div>
        </div>
    </div>

    <!-- ===== SCREEN: WALLET (CASHIER) ===== -->
    <div class="screen" id="scrWallet">
        <!-- Cashier Header -->
        <div style="padding:16px 16px 8px">
            <h2 style="font-family:'Montserrat',sans-serif;font-size:22px;font-weight:900;margin:0">Cashier</h2>
        </div>

        <!-- Dual balance cards -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:0 16px 12px">
            <div onclick="switchActiveWallet('usdt')"
                style="padding:14px;background:var(--surface);border:1.5px solid var(--border);border-radius:var(--radius-lg);cursor:pointer;transition:all .15s"
                id="cashierUsdtCard">
                <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px">
                    <span style="font-size:16px">💵</span>
                    <span
                        style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:1px;color:var(--dim)">CRYPTO</span>
                </div>
                <div style="font-family:'Montserrat',sans-serif;font-size:20px;font-weight:900;color:#fff"
                    id="wBalAmount">0.00</div>
                <div style="font-size:10px;color:var(--dim);margin-top:2px" id="wBalUnit">USDT</div>
            </div>
            <div onclick="switchActiveWallet('stars')"
                style="padding:14px;background:var(--surface);border:1.5px solid var(--border);border-radius:var(--radius-lg);cursor:pointer;transition:all .15s"
                id="cashierStarsCard">
                <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px">
                    <span style="font-size:16px">⭐</span>
                    <span
                        style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:1px;color:var(--dim)">STARS</span>
                </div>
                <div style="font-family:'Montserrat',sans-serif;font-size:20px;font-weight:900;color:#FFD700"
                    id="wStarsAmount">0</div>
                <div style="font-size:10px;color:var(--dim);margin-top:2px">Stars</div>
            </div>
        </div>

        <!-- Currency display switcher -->
        <div style="display:flex;gap:6px;padding:0 16px 12px;justify-content:center;flex-wrap:wrap" id="currencyRow">
            <button class="pill active" onclick="setCurrency('USDT')" data-cur="USDT"
                style="font-size:10px;height:26px;padding:0 10px">USDT</button>
            <button class="pill" onclick="setCurrency('USD')" data-cur="USD"
                style="font-size:10px;height:26px;padding:0 10px">USD</button>
            <button class="pill" onclick="setCurrency('PLN')" data-cur="PLN"
                style="font-size:10px;height:26px;padding:0 10px">PLN</button>
            <button class="pill" onclick="setCurrency('UAH')" data-cur="UAH"
                style="font-size:10px;height:26px;padding:0 10px">UAH</button>
            <button class="pill" onclick="setCurrency('EUR')" data-cur="EUR"
                style="font-size:10px;height:26px;padding:0 10px">EUR</button>
        </div>

        <!-- 3 Main Tabs: Deposit / Withdraw / History -->
        <div
            style="display:flex;gap:0;margin:0 16px 16px;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden">
            <div class="tw-tab active" onclick="switchCashierTab('deposit')" id="cashTabDeposit"
                style="flex:1;padding:10px 0;text-align:center;font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.5px;color:var(--dim);cursor:pointer;transition:all .15s;border-right:1px solid var(--border)">
                Deposit</div>
            <div class="tw-tab" onclick="switchCashierTab('withdraw')" id="cashTabWithdraw"
                style="flex:1;padding:10px 0;text-align:center;font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.5px;color:var(--dim);cursor:pointer;transition:all .15s;border-right:1px solid var(--border)">
                Withdraw</div>
            <div class="tw-tab" onclick="switchCashierTab('history')" id="cashTabHistory"
                style="flex:1;padding:10px 0;text-align:center;font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.5px;color:var(--dim);cursor:pointer;transition:all .15s">
                History</div>
        </div>

        <!-- ====== DEPOSIT TAB ====== -->
        <div id="cashDeposit">
            <!-- Payment methods -->
            <div style="padding:0 16px;margin-bottom:12px">
                <div style="font-size:9px;font-weight:800;text-transform:uppercase;letter-spacing:1.5px;color:var(--dim);font-family:'Montserrat',sans-serif;margin-bottom:10px"
                    id="wMethodLabel">PAYMENT METHOD</div>
                <div style="display:flex;flex-direction:column;gap:8px">
                    <!-- CryptoBot -->
                    <button class="card"
                        style="display:flex;align-items:center;gap:12px;padding:14px 16px;cursor:pointer;border:1.5px solid var(--red);transition:all .15s"
                        id="pmCrypto" onclick="selectPayMethod('crypto')">
                        <div
                            style="width:40px;height:40px;border-radius:10px;background:rgba(227,30,36,.08);display:flex;align-items:center;justify-content:center;flex-shrink:0">
                            <span style="font-size:20px">💎</span>
                        </div>
                        <div style="flex:1">
                            <div style="display:flex;align-items:center;gap:6px">
                                <span style="font-size:13px;font-weight:700">CryptoBot</span>
                                <span
                                    style="font-size:9px;font-weight:800;color:var(--green);background:rgba(34,197,94,.1);padding:2px 6px;border-radius:4px">🔥
                                    +7%</span>
                            </div>
                            <div style="font-size:10px;color:var(--dim)">USDT, BTC, TON · Min $1.00</div>
                        </div>
                        <span class="material-symbols-outlined"
                            style="color:var(--red);font-size:18px">check_circle</span>
                    </button>
                    <!-- Telegram Stars -->
                    <button class="card"
                        style="display:flex;align-items:center;gap:12px;padding:14px 16px;cursor:pointer;transition:all .15s"
                        id="pmStars" onclick="selectPayMethod('stars')">
                        <div
                            style="width:40px;height:40px;border-radius:10px;background:rgba(255,215,0,.08);display:flex;align-items:center;justify-content:center;flex-shrink:0">
                            <span style="font-size:20px">⭐</span>
                        </div>
                        <div style="flex:1">
                            <div style="font-size:13px;font-weight:700">Telegram Stars</div>
                            <div style="font-size:10px;color:var(--dim)">Instant · In-app payment</div>
                        </div>
                        <span class="material-symbols-outlined" style="color:var(--dim);font-size:18px"
                            id="pmStarsCheck">radio_button_unchecked</span>
                    </button>
                    <!-- Bank Card -->
                    <button class="card"
                        style="display:flex;align-items:center;gap:12px;padding:14px 16px;cursor:pointer;transition:all .15s;opacity:.5"
                        id="pmCard" onclick="selectPayMethod('card')">
                        <div
                            style="width:40px;height:40px;border-radius:10px;background:rgba(59,130,246,.08);display:flex;align-items:center;justify-content:center;flex-shrink:0">
                            <span style="font-size:20px">💳</span>
                        </div>
                        <div style="flex:1">
                            <div style="font-size:13px;font-weight:700" id="pmCardTitle">Bank Card</div>
                            <div style="font-size:10px;color:var(--dim)">Visa, Mastercard · Coming soon</div>
                        </div>
                        <span class="material-symbols-outlined" style="color:var(--dim);font-size:18px"
                            id="pmCardCheck">radio_button_unchecked</span>
                    </button>
                </div>
            </div>

            <!-- Deposit packages (crypto) -->
            <div id="depositCryptoSection">
                <div class="wallet-assets">
                    <div class="wallet-assets-label" id="wPkgLabel">SELECT PACKAGE</div>
                    <div class="asset-row" id="assetRow"></div>
                </div>
                <!-- Crypto bonus info -->
                <div
                    style="margin:8px 16px 12px;padding:10px 12px;background:rgba(34,197,94,.04);border:1px solid rgba(34,197,94,.12);border-radius:var(--radius);display:flex;align-items:center;gap:8px">
                    <span style="font-size:14px">🎁</span>
                    <div style="font-size:10px;color:var(--dim);line-height:1.4">Your deposit will receive <b
                            style="color:var(--green)">+7% bonus</b> with <b>x3 wager</b> requirement</div>
                </div>
            </div>

            <!-- Stars packages -->
            <div id="depositStarsSection" style="display:none">
                <div class="wallet-assets">
                    <div class="wallet-assets-label">SELECT STARS PACKAGE</div>
                    <div class="asset-row" id="starsRow"></div>
                </div>
                <div style="padding:0 16px;margin-top:8px">
                    <div class="dc-note"><span class="material-symbols-outlined">info</span>
                        <p>Stars are purchased via Telegram. Stars balance is independent from USDT/Crypto.</p>
                    </div>
                </div>
            </div>

            <!-- Deposit Button -->
            <div style="padding:16px">
                <button class="btn-primary" onclick="openDepositModal(payMethod === 'stars' ? 'stars' : 'usdt')"
                    style="height:48px;font-size:14px;border-radius:12px;width:100%">
                    <span class="material-symbols-outlined" style="font-size:18px">arrow_downward</span>
                    <span id="wDeposit">DEPOSIT NOW</span>
                </button>
            </div>
        </div>

        <!-- ====== WITHDRAW TAB ====== -->
        <div id="cashWithdraw" style="display:none;padding:0 16px">
            <div style="padding:12px 0">
                <div
                    style="font-size:9px;font-weight:800;text-transform:uppercase;letter-spacing:1.5px;color:var(--dim);font-family:'Montserrat',sans-serif;margin-bottom:12px">
                    WITHDRAW FUNDS</div>

                <!-- Method selector -->
                <div style="display:flex;gap:8px;margin-bottom:16px">
                    <button class="pill active" id="wdCrypto" onclick="selectWithdrawMethod('crypto')"
                        style="flex:1;justify-content:center;height:36px">💎 CryptoBot</button>
                    <button class="pill" id="wdStars" onclick="selectWithdrawMethod('stars')"
                        style="flex:1;justify-content:center;height:36px">⭐ Stars</button>
                </div>

                <!-- Amount input -->
                <div
                    style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-lg);padding:16px;margin-bottom:12px">
                    <div
                        style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:1px;color:var(--dim);margin-bottom:8px">
                        AMOUNT</div>
                    <div style="display:flex;align-items:center;gap:8px">
                        <input type="number" id="withdrawAmount" value="10.00" min="1" step="0.01"
                            style="flex:1;background:transparent;border:none;color:#fff;font-family:'Montserrat',sans-serif;font-weight:800;font-size:24px;outline:none;width:100%">
                        <span
                            style="font-family:'Montserrat',sans-serif;font-weight:800;color:var(--dim);font-size:14px"
                            id="wdUnit">USDT</span>
                    </div>
                    <div style="display:flex;gap:6px;margin-top:10px">
                        <button class="pill" onclick="setWithdrawPct(25)"
                            style="flex:1;justify-content:center;height:28px;font-size:10px">25%</button>
                        <button class="pill" onclick="setWithdrawPct(50)"
                            style="flex:1;justify-content:center;height:28px;font-size:10px">50%</button>
                        <button class="pill" onclick="setWithdrawPct(75)"
                            style="flex:1;justify-content:center;height:28px;font-size:10px">75%</button>
                        <button class="pill" onclick="setWithdrawPct(100)"
                            style="flex:1;justify-content:center;height:28px;font-size:10px">MAX</button>
                    </div>
                </div>

                <!-- Withdraw info -->
                <div
                    style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:12px;margin-bottom:12px">
                    <div style="display:flex;justify-content:space-between;margin-bottom:6px">
                        <span style="font-size:11px;color:var(--dim)">Available</span>
                        <span style="font-size:11px;font-weight:700;color:#fff" id="wdAvailable">0.00 USDT</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;margin-bottom:6px">
                        <span style="font-size:11px;color:var(--dim)">Min withdrawal</span>
                        <span style="font-size:11px;font-weight:700;color:var(--dim)">$5.00</span>
                    </div>
                    <div style="display:flex;justify-content:space-between">
                        <span style="font-size:11px;color:var(--dim)">Fee</span>
                        <span style="font-size:11px;font-weight:700;color:var(--green)">FREE</span>
                    </div>
                </div>

                <button class="btn-primary" onclick="submitWithdraw()"
                    style="height:48px;font-size:14px;border-radius:12px;width:100%">
                    <span class="material-symbols-outlined" style="font-size:18px">arrow_upward</span>
                    WITHDRAW
                </button>

                <!-- Wager warning -->
                <div
                    style="margin-top:12px;padding:10px;background:rgba(227,30,36,.04);border:1px solid rgba(227,30,36,.1);border-radius:var(--radius);display:flex;align-items:center;gap:8px">
                    <span class="material-symbols-outlined" style="font-size:16px;color:var(--red)">warning</span>
                    <div style="font-size:10px;color:var(--dim);line-height:1.4">Bonus funds require <b>x3 wagering</b>
                        before withdrawal. Active bonuses will be forfeited.</div>
                </div>
            </div>
        </div>

        <!-- ====== HISTORY TAB ====== -->
        <div id="cashHistory" style="display:none;padding:0 16px">
            <div style="padding:12px 0">
                <div
                    style="font-size:9px;font-weight:800;text-transform:uppercase;letter-spacing:1.5px;color:var(--dim);font-family:'Montserrat',sans-serif;margin-bottom:12px">
                    TRANSACTION HISTORY</div>
                <div id="txHistoryList">
                    <div style="text-align:center;padding:40px 0;opacity:.4">
                        <span class="material-symbols-outlined"
                            style="font-size:40px;display:block;margin-bottom:6px">receipt_long</span>
                        <span style="font-size:12px">No transactions yet</span>
                    </div>
                </div>
            </div>
        </div>

        <div style="height:20px"></div>
    </div>

    <!-- ===== SCREEN: REFERRAL ===== -->
    <div class="screen" id="scrReferral">
        <div class="ref-hero">
            <div class="ref-hero-icon"><img
                    src="https://lh3.googleusercontent.com/aida-public/AB6AXuCpCm-In3qaads4-907wOGoyxZRtNhNrOWD-U1kAC57uAA0oO3DnPwchxZ4EraGR6QuJgvoSYkYmuPig3Bi5g-ROCe5cnWc_zg4Jis0UHe8n3saeShVPK2gJ4DXrXcOK-M2IjhFYujSo3fc2HFsdKyGllktDw2yiUFcLx0VlGohAFPIZdJjzEn-_bw47k35CYqzdnl6tKITBGL_Jdj7BNOqIkQ5uK71RWcXAWNxEJtmUIMLeNmbVOuLBo45VWiYk9VAWFqJvWBhpeY"
                    alt="Coins"
                    style="width:100px;height:100px;object-fit:contain;filter:drop-shadow(0 8px 16px rgba(227,30,36,.3))">
            </div>
            <h1 id="refHeroTitle">Invite & <span>Earn</span></h1>
            <p id="refHeroDesc">Share your link and earn <b>10 coins</b> for every friend who plays.</p>
        </div>

        <div class="ref-link-card">
            <div class="ref-link-inner">
                <div class="ref-link-label" id="refLinkLabel">TAP COPY TO SHARE</div>
                <div class="ref-link-box">
                    <div class="ref-url" id="refUrl">https://t.me/bot?start=ref...</div>
                    <button class="ref-copy" onclick="copyRefLink()"><span
                            class="material-symbols-outlined">content_copy</span><span
                            id="refCopyText">Copy</span></button>
                </div>
            </div>
        </div>

        <div class="ref-stats">
            <div class="ref-stat-card">
                <div class="ref-stat-top">
                    <div class="ref-stat-icon people"><span class="material-symbols-outlined">group_add</span></div>
                    <div class="ref-stat-badge" id="refNewBadge"></div>
                </div>
                <div class="ref-stat-label" id="refTotalLabel">Total Referrals</div>
                <div class="ref-stat-val" id="refTotalVal">0</div>
            </div>
            <div class="ref-stat-card">
                <div class="ref-stat-top">
                    <div class="ref-stat-icon money"><span
                            class="material-symbols-outlined">account_balance_wallet</span></div>
                </div>
                <div class="ref-stat-label" id="refEarnedLabel">Earned Coins</div>
                <div class="ref-stat-val" id="refEarnedVal">0</div>
            </div>
        </div>

        <div class="ref-how">
            <div class="ref-how-title" id="refHowTitle">How it Works</div>
            <div class="ref-steps">
                <div class="ref-step">
                    <div class="ref-step-line">
                        <div class="ref-step-num">1</div>
                        <div class="ref-step-connector"></div>
                    </div>
                    <div class="ref-step-content">
                        <h3 id="refStep1T">Share with friends</h3>
                        <p id="refStep1D">Send your unique link via Telegram or social media.</p>
                    </div>
                </div>
                <div class="ref-step">
                    <div class="ref-step-line">
                        <div class="ref-step-num">2</div>
                        <div class="ref-step-connector"></div>
                    </div>
                    <div class="ref-step-content">
                        <h3 id="refStep2T">Friends start playing</h3>
                        <p id="refStep2D">When they register, you both get bonus coins.</p>
                    </div>
                </div>
                <div class="ref-step">
                    <div class="ref-step-line">
                        <div class="ref-step-num">3</div>
                    </div>
                    <div class="ref-step-content">
                        <h3 id="refStep3T">Earn Rewards</h3>
                        <p id="refStep3D">Get 10 coins for every friend who joins.</p>
                    </div>
                </div>
            </div>
        </div>

        <button class="ref-share-btn" onclick="shareRef()"><span class="material-symbols-outlined">ios_share</span><span
                id="refShareBtn">Share Link Now</span></button>
    </div>

    <!-- ===== SCREEN: PROFILE ===== -->
    <div class="screen" id="scrProfile">
        <div class="prof-header">
            <div class="prof-avatar">
                <div class="prof-avatar-inner" id="profAvatarInner"><img
                        src="https://lh3.googleusercontent.com/aida-public/AB6AXuDr3zsmMzZoKQBmXyKeYm7wjdUyCdTgqgmWcGFJrHZ1j04p23PyhyC-veLVchduXKVpILhD8OvgoBIY1kOdWCDOIZgRURbE4kJTa5KugjgI2XTZ2f-Atab5Y1nG3egXh_6wk1yFwzjlyBkkbJ3ID-hqkVSJfimD4Exhl70tk5RZYzwUAQXuY1t0RWIhqsrPPWPeni-TFGVUKHJ7X0JKR0ANZAZXV9wWgMeBNnOzlApLWWe8wo3HJ13XCqJvvsTxAsyt3XT5UdULBhM"
                        alt="Avatar" style="width:100%;height:100%;object-fit:cover"></div>
            </div>
            <div class="prof-name" id="profName">Player</div>
            <div class="prof-meta">
                <span class="prof-id" id="profId">ID: ...</span>
                <span style="width:1px;height:14px;background:var(--surface2)"></span>
                <span class="prof-vip-badge"><span class="material-symbols-outlined">stars</span><span
                        id="profVipBadge">VIP</span></span>
            </div>
        </div>

        <div class="prof-level">
            <div class="prof-level-top">
                <div class="prof-level-name" id="profLevelName">Bronze</div>
                <div class="prof-level-val" id="profLevelVal">Level 1</div>
            </div>
            <div class="vip-bar">
                <div class="vip-bar-fill" id="profVipBar" style="width:0%"></div>
            </div>
            <div class="prof-level-xp"><span id="profXpLabel">Current XP</span><span id="profXpVal">0 / 1000</span>
            </div>
        </div>

        <div class="prof-stats">
            <div class="prof-stat">
                <div class="prof-stat-label" id="stWinsL">WINS</div>
                <div class="prof-stat-val" id="stWins">0</div>
            </div>
            <div class="prof-stat">
                <div class="prof-stat-label" id="stLossesL">LOSSES</div>
                <div class="prof-stat-val" id="stLosses">0</div>
            </div>
            <div class="prof-stat">
                <div class="prof-stat-label" id="stTotalL">TOTAL</div>
                <div class="prof-stat-val" id="stTotal">0</div>
            </div>
        </div>

        <div
            style="margin:20px 16px 12px;padding:16px;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-lg)">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px">
                <h3 style="font-family:'Montserrat',sans-serif;font-size:14px;font-weight:800;color:#fff">My Bonuses
                </h3>
                <span style="font-size:10px;color:var(--dim2);text-transform:uppercase;font-weight:800">Available</span>
            </div>

            <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px">
                <div
                    style="width:40px;height:40px;border-radius:10px;background:rgba(227,30,36,.1);display:flex;align-items:center;justify-content:center">
                    <span class="material-symbols-outlined" style="color:var(--red)">redeem</span>
                </div>
                <div>
                    <div
                        style="font-size:10px;color:var(--dim);text-transform:uppercase;letter-spacing:1px;font-weight:600;margin-bottom:2px">
                        Bonus Balance</div>
                    <div style="font-family:'Montserrat',sans-serif;font-size:18px;font-weight:800;color:#fff"
                        id="bonusBalAmount">$0.00</div>
                </div>
            </div>

            <div id="activeBonusList" style="display:flex;flex-direction:column;gap:10px;margin-bottom:12px"></div>

            <button onclick="nav('bonuses')"
                style="width:100%;padding:12px;background:none;border:1px solid rgba(227,30,36,.3);border-radius:var(--radius);color:var(--red);font-family:'Montserrat',sans-serif;font-size:12px;font-weight:700;cursor:pointer;transition:all .15s">VIEW
                ALL OFFERS</button>
        </div>

        <div class="prof-referral-btn" onclick="nav('referral')">
            <div class="prof-ref-left">
                <div class="prof-ref-icon"><span class="material-symbols-outlined">diversity_3</span></div>
                <div class="prof-ref-text">
                    <h3 id="profRefTitle">Referral Program</h3>
                    <p id="profRefSub">Invite friends & earn rewards</p>
                </div>
            </div>
            <span class="material-symbols-outlined">arrow_forward</span>
        </div>

        <div class="prof-menu">
            <div class="prof-menu-item" onclick="openLangSelector()">
                <div class="prof-menu-left"><span class="material-symbols-outlined">language</span><span
                        id="profLang">Language</span></div>
                <div style="display:flex;align-items:center;gap:4px"><span id="profLangCurrent"
                        style="font-size:12px;color:var(--dim)"></span><span
                        class="material-symbols-outlined">chevron_right</span></div>
            </div>
            <div class="prof-menu-item" onclick="changeLang()">
                <div class="prof-menu-left"><span class="material-symbols-outlined">settings</span><span
                        id="profSettings">Settings</span></div><span
                    class="material-symbols-outlined">chevron_right</span>
            </div>
            <div class="prof-menu-item">
                <div class="prof-menu-left"><span class="material-symbols-outlined">security</span><span
                        id="profSecurity">Security</span></div><span
                    class="material-symbols-outlined">chevron_right</span>
            </div>
            <div class="prof-menu-item">
                <div class="prof-menu-left"><span class="material-symbols-outlined">headset_mic</span><span
                        id="profSupport">Support</span></div><span
                    class="material-symbols-outlined">chevron_right</span>
            </div>
        </div>

        <!-- Language selector overlay -->
        <div id="langOverlay"
            style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.8);z-index:300;align-items:flex-end;justify-content:center">
            <div
                style="background:var(--surface);border-top-left-radius:var(--radius-xl);border-top-right-radius:var(--radius-xl);width:100%;max-width:480px;padding:20px 16px 32px">
                <div style="width:40px;height:4px;background:var(--surface3);border-radius:2px;margin:0 auto 16px">
                </div>
                <h3 style="font-family:'Montserrat',sans-serif;font-size:16px;font-weight:800;margin-bottom:16px;text-align:center"
                    id="langTitle">Select Language</h3>
                <div style="display:flex;flex-direction:column;gap:6px" id="langList"></div>
            </div>
        </div>

        <button class="prof-signout" id="profSignout">Sign Out</button>
    </div>

    <!-- ===== BOTTOM NAV ===== -->
    <div class="bottom-nav">
        <div class="nav-item active group" data-screen="lobby"
            onclick="nav('lobby'); if(window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.HapticFeedback){window.Telegram.WebApp.HapticFeedback.impactOccurred('light')}">
            <span class="material-symbols-outlined">home</span>
            <div class="nav-label" id="navLobby">Home</div>
            <div class="nav-indicator"></div>
        </div>
        <div class="nav-item group" data-screen="game"
            onclick="nav('game'); if(window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.HapticFeedback){window.Telegram.WebApp.HapticFeedback.impactOccurred('light')}">
            <span class="material-symbols-outlined">casino</span>
            <div class="nav-label" id="navGame">Games</div>
            <div class="nav-indicator"></div>
        </div>
        <div class="nav-item group" data-screen="bonuses" style="position:relative"
            onclick="nav('bonuses'); if(window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.HapticFeedback){window.Telegram.WebApp.HapticFeedback.impactOccurred('light')}">
            <span class="material-symbols-outlined">redeem</span>
            <div class="nav-badge" id="bonusBadge" style="display:none">0</div>
            <div class="nav-label" id="navBonuses">Bonuses</div>
            <div class="nav-indicator"></div>
        </div>
        <div class="nav-item group" data-screen="wallet"
            onclick="nav('wallet'); if(window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.HapticFeedback){window.Telegram.WebApp.HapticFeedback.impactOccurred('light')}">
            <span class="material-symbols-outlined">account_balance_wallet</span>
            <div class="nav-label" id="navWallet">Wallet</div>
            <div class="nav-indicator"></div>
        </div>
        <div class="nav-item group" data-screen="profile"
            onclick="nav('profile'); if(window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.HapticFeedback){window.Telegram.WebApp.HapticFeedback.impactOccurred('light')}">
            <span class="material-symbols-outlined">person</span>
            <div class="nav-label" id="navProfile">Profile</div>
            <div class="nav-indicator"></div>
        </div>
    </div>

    <!-- ===== BONUS OVERLAY ===== -->
    <div class="bonus-overlay" id="bonusOL">
        <div class="bo-title" id="boTitle">🎰 BONUS ROUND 🎰</div>
        <div class="bo-info">
            <div class="bo-info-item">
                <div class="label" id="boSpinL">SPIN</div>
                <div class="val" id="boSpinC">0/10</div>
            </div>
            <div class="bo-info-item">
                <div class="label" id="boTotalL">WIN</div>
                <div class="val" id="boRunT">0</div>
            </div>
        </div>
        <div class="bo-grid-wrap">
            <div class="bo-grid" id="boGrid"></div>
        </div>
        <div class="bo-result" id="boRes"></div>
        <div class="bo-total" id="boFinal"></div>
        <button class="bo-close" id="boClose" onclick="closeBonus()">COLLECT 🪙</button>
    </div>

    <!-- ===== TOAST ===== -->
    <div class="toast" id="toast">
        <div class="toast-icon" id="toastIcon">💰</div>
        <div class="toast-text" id="toastText">Not enough coins!</div>
        <div class="toast-btns">
            <button class="toast-btn secondary" onclick="closeToast()" id="toastCancel">✕</button>
            <button class="toast-btn primary" onclick="toastAction()" id="toastOk">Deposit</button>
        </div>
    </div>

    <!-- ===== FORTUNE WHEEL OVERLAY ===== -->
    <div id="wheelOL" style="display:none;position:fixed;inset:0;z-index:200;background:#121212;overflow-y:auto">
        <!-- Sparkle decorations -->
        <div
            style="position:absolute;inset:0;pointer-events:none;background-image:radial-gradient(circle at 20% 30%,rgba(227,28,35,.12) 0%,transparent 25%),radial-gradient(circle at 80% 70%,rgba(255,215,0,.03) 0%,transparent 25%)">
        </div>
        <div
            style="position:absolute;top:80px;right:48px;color:#FFD700;opacity:.1;font-size:36px;animation:pulse 2s infinite">
            ✦</div>

        <!-- Header -->
        <div
            style="display:flex;align-items:center;justify-content:space-between;padding:24px 20px 16px;position:relative;z-index:10">
            <button onclick="closeWheel()"
                style="width:40px;height:40px;border-radius:50%;background:rgba(33,17,18,.8);border:1px solid rgba(255,255,255,.05);color:rgba(255,255,255,.7);display:flex;align-items:center;justify-content:center;cursor:pointer">
                <span class="material-symbols-outlined">close</span>
            </button>
            <h2
                style="font-family:'Montserrat',sans-serif;font-size:18px;font-weight:800;color:#fff;text-transform:uppercase;letter-spacing:.5px">
                RubyBet</h2>
            <div
                style="display:flex;align-items:center;gap:8px;background:rgba(33,17,18,.8);border:1px solid rgba(255,255,255,.1);border-radius:9999px;padding:6px 12px">
                <span class="material-symbols-outlined" style="font-size:18px;color:#FFD700">stars</span>
                <span id="wheelBalDisplay"
                    style="font-size:12px;font-weight:700;color:#fff;font-family:'Montserrat',sans-serif">0</span>
            </div>
        </div>

        <!-- SPIN STATE -->
        <div id="wheelSpinState"
            style="position:relative;z-index:10;display:flex;flex-direction:column;align-items:center;padding:16px 24px 48px">
            <div style="text-align:center;margin-bottom:24px">
                <h1
                    style="font-family:'Montserrat',sans-serif;font-size:28px;font-weight:900;color:#fff;text-transform:uppercase;font-style:italic;text-shadow:0 4px 20px rgba(227,28,35,.6);letter-spacing:-1px">
                    Daily Wheel</h1>
                <p
                    style="color:rgba(255,255,255,.5);font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:2px;margin-top:8px">
                    Spin to win exclusive rewards</p>
            </div>

            <!-- Wheel -->
            <div id="wheelVisual" style="position:relative;width:300px;height:300px;margin:0 auto 32px">
                <!-- Pointer -->
                <div style="position:absolute;top:-12px;left:50%;transform:translateX(-50%);z-index:30">
                    <svg width="36" height="44" viewBox="0 0 40 50" fill="none">
                        <path d="M20 50L5 15C5 15 0 5 10 5H30C40 5 35 15 35 15L20 50Z" fill="#F8F6F6" stroke="#211112"
                            stroke-width="2" />
                        <circle cx="20" cy="10" r="5" fill="#e31c23" />
                    </svg>
                </div>
                <!-- Outer Rim -->
                <div
                    style="position:absolute;inset:0;border-radius:50%;background:linear-gradient(145deg,#2a1a1a,#110d0d);box-shadow:0 0 0 6px #1a1a1a,0 0 0 8px #e31c23,0 0 30px 5px rgba(227,28,35,.5);display:flex;align-items:center;justify-content:center;overflow:hidden">
                    <!-- Bulbs -->
                    <div class="wh-bulb" style="top:8px;left:50%;transform:translateX(-50%)"></div>
                    <div class="wh-bulb" style="bottom:8px;left:50%;transform:translateX(-50%)"></div>
                    <div class="wh-bulb" style="top:25%;right:8%"></div>
                    <div class="wh-bulb" style="top:25%;left:8%"></div>
                    <div class="wh-bulb" style="bottom:25%;right:8%"></div>
                    <div class="wh-bulb" style="bottom:25%;left:8%"></div>
                    <div class="wh-bulb" style="top:50%;right:4px;transform:translateY(-50%)"></div>
                    <div class="wh-bulb" style="top:50%;left:4px;transform:translateY(-50%)"></div>
                    <div class="wh-bulb" style="top:8%;right:25%"></div>
                    <div class="wh-bulb" style="top:8%;left:25%"></div>
                    <div class="wh-bulb" style="bottom:8%;right:25%"></div>
                    <div class="wh-bulb" style="bottom:8%;left:25%"></div>

                    <!-- Segments disc (this rotates) -->
                    <div id="wheelDisc"
                        style="width:92%;height:92%;border-radius:50%;background:conic-gradient(#e31c23 0deg 60deg,#232323 60deg 120deg,#e31c23 120deg 180deg,#232323 180deg 240deg,#e31c23 240deg 300deg,#232323 300deg 360deg);position:relative;box-shadow:inset 0 0 25px rgba(0,0,0,.9);border:2px solid rgba(255,255,255,.1);transition:transform 4s cubic-bezier(.17,.67,.05,.99)">
                        <!-- Segment labels -->
                        <div class="wh-seg" style="transform:rotate(30deg)">
                            <div class="wh-seg-inner"><span class="material-symbols-outlined"
                                    style="font-size:24px;color:#fff">payments</span><span
                                    class="wh-seg-label">CASH</span></div>
                        </div>
                        <div class="wh-seg" style="transform:rotate(90deg)">
                            <div class="wh-seg-inner"><span class="material-symbols-outlined"
                                    style="font-size:24px;color:#FFD700">casino</span><span
                                    class="wh-seg-label">SPINS</span></div>
                        </div>
                        <div class="wh-seg" style="transform:rotate(150deg)">
                            <div class="wh-seg-inner"><span class="material-symbols-outlined"
                                    style="font-size:24px;color:#fff">percent</span><span
                                    class="wh-seg-label">DEPOSIT</span></div>
                        </div>
                        <div class="wh-seg" style="transform:rotate(210deg)">
                            <div class="wh-seg-inner"><span class="material-symbols-outlined"
                                    style="font-size:24px;color:#FFD700">stars</span><span
                                    class="wh-seg-label">STARS</span></div>
                        </div>
                        <div class="wh-seg" style="transform:rotate(270deg)">
                            <div class="wh-seg-inner"><span class="material-symbols-outlined"
                                    style="font-size:24px;color:#fff">diamond</span><span
                                    class="wh-seg-label">VIP</span></div>
                        </div>
                        <div class="wh-seg" style="transform:rotate(330deg)">
                            <div class="wh-seg-inner"><span class="material-symbols-outlined"
                                    style="font-size:24px;color:#FFD700">inventory_2</span><span
                                    class="wh-seg-label">MYSTERY</span></div>
                        </div>
                    </div>
                </div>
                <!-- Center button -->
                <div
                    style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:60px;height:60px;background:radial-gradient(circle at 30% 30%,#ff4d4d,#8a1014);border-radius:50%;box-shadow:0 4px 15px rgba(0,0,0,.6),inset 0 2px 5px rgba(255,255,255,.4);z-index:20;border:4px solid #fff;display:flex;align-items:center;justify-content:center">
                    <span class="material-symbols-outlined"
                        style="color:#fff;font-size:28px;text-shadow:0 2px 4px rgba(0,0,0,.3)">bolt</span>
                </div>
            </div>

            <!-- Spin Button -->
            <button id="wheelSpinBtn" onclick="doWheelSpin()"
                style="width:100%;max-width:300px;padding:16px;border-radius:9999px;border:none;background:#e31c23;color:#fff;font-family:'Montserrat',sans-serif;font-size:18px;font-weight:900;text-transform:uppercase;letter-spacing:2px;cursor:pointer;box-shadow:0 0 20px rgba(227,28,35,.6),0 0 40px rgba(227,28,35,.3);transition:all .2s;border-top:1px solid rgba(255,255,255,.2);position:relative;overflow:hidden">
                <span id="wheelSpinBtnText">SPIN FOR FREE</span>
                <span class="material-symbols-outlined" style="margin-left:8px;vertical-align:middle">cached</span>
            </button>

            <!-- Timer -->
            <div
                style="margin-top:20px;display:flex;align-items:center;gap:8px;color:rgba(255,255,255,.5);font-size:14px;font-weight:500;background:rgba(255,255,255,.05);padding:6px 16px;border-radius:9999px;border:1px solid rgba(255,255,255,.05)">
                <span class="material-symbols-outlined" style="font-size:14px">schedule</span>
                <span>Next spin in <span id="wheelTimer" style="color:#fff;font-family:monospace">24:00:00</span></span>
            </div>
        </div>

        <!-- WIN STATE -->
        <div id="wheelWinState"
            style="display:none;position:absolute;inset:0;z-index:50;display:none;flex-direction:column;align-items:center;justify-content:center;padding:24px">
            <div style="position:absolute;inset:0;background:rgba(0,0,0,.6);backdrop-filter:blur(2px)"></div>
            <div
                style="position:relative;z-index:10;width:100%;max-width:320px;background:rgba(33,17,18,.95);backdrop-filter:blur(20px);border-radius:24px;padding:48px 24px 32px;display:flex;flex-direction:column;align-items:center;text-align:center;border:1px solid #e31c23;box-shadow:0 0 25px rgba(227,30,36,.5),inset 0 0 40px rgba(0,0,0,.9)">
                <div style="position:relative;margin-bottom:16px">
                    <div
                        style="position:absolute;inset:0;background:rgba(255,215,0,.2);filter:blur(20px);border-radius:50%">
                    </div>
                    <span class="material-symbols-outlined"
                        style="font-size:96px;font-variation-settings:'FILL' 1,'wght' 700;background:linear-gradient(135deg,#FFD700,#FDB931);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 20px rgba(255,215,0,.5));position:relative;z-index:10">stars</span>
                </div>
                <h1
                    style="font-family:'Montserrat',sans-serif;font-size:24px;font-weight:900;color:#fff;text-transform:uppercase;letter-spacing:2px;margin-bottom:12px">
                    CONGRATULATIONS!</h1>
                <p
                    style="font-family:'Montserrat',sans-serif;font-size:14px;font-weight:700;color:rgba(255,255,255,.6);text-transform:uppercase;letter-spacing:2px;margin-bottom:8px">
                    You won</p>
                <div id="wheelWinAmount"
                    style="font-family:'Montserrat',sans-serif;font-size:60px;font-weight:900;color:#fff;text-shadow:0 0 20px rgba(227,28,35,.8);letter-spacing:-2px;margin-bottom:4px">
                    500</div>
                <p id="wheelWinUnit"
                    style="font-family:'Montserrat',sans-serif;font-size:14px;font-weight:700;color:rgba(255,255,255,.5);text-transform:uppercase;letter-spacing:4px;margin-bottom:32px">
                    STARS</p>
                <button onclick="collectWheelPrize()"
                    style="width:100%;padding:16px;border-radius:12px;border:none;background:#e31c23;color:#fff;font-family:'Montserrat',sans-serif;font-size:18px;font-weight:800;text-transform:uppercase;letter-spacing:2px;cursor:pointer;box-shadow:0 0 20px rgba(227,28,35,.6),0 0 40px rgba(227,28,35,.3);position:relative;overflow:hidden">COLLECT</button>
            </div>
        </div>

        <!-- LOCKED STATE -->
        <div id="wheelLockedState"
            style="display:none;position:absolute;inset:0;z-index:50;display:none;flex-direction:column;align-items:center;justify-content:center;padding:24px">
            <div style="position:absolute;inset:0;background:rgba(0,0,0,.6);backdrop-filter:blur(2px)"></div>
            <div
                style="position:relative;z-index:10;width:100%;max-width:320px;background:rgba(33,17,18,.95);backdrop-filter:blur(20px);border-radius:24px;padding:48px 24px 32px;display:flex;flex-direction:column;align-items:center;text-align:center;border:1px solid #e31c23;box-shadow:0 0 25px rgba(227,30,36,.5),inset 0 0 40px rgba(0,0,0,.9)">
                <div style="position:relative;margin-bottom:16px">
                    <div
                        style="position:absolute;inset:0;background:rgba(227,28,35,.2);filter:blur(20px);border-radius:50%">
                    </div>
                    <span class="material-symbols-outlined"
                        style="font-size:96px;font-variation-settings:'FILL' 1,'wght' 700;background:linear-gradient(135deg,#e31c23,#ff6b6b);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 25px rgba(227,28,35,.8));position:relative;z-index:10">lock_clock</span>
                </div>
                <h1
                    style="font-family:'Montserrat',sans-serif;font-size:28px;font-weight:900;color:#fff;text-transform:uppercase;letter-spacing:2px;margin-bottom:24px">
                    LOCKED</h1>
                <p
                    style="font-family:'Montserrat',sans-serif;font-size:12px;font-weight:700;color:rgba(255,255,255,.6);text-transform:uppercase;letter-spacing:4px;margin-bottom:12px">
                    NEXT FREE SPIN IN:</p>
                <div id="wheelLockedTimer"
                    style="font-family:'Montserrat',sans-serif;font-size:32px;font-weight:900;color:#fff;text-shadow:0 0 15px rgba(255,255,255,.4),0 0 8px rgba(227,28,35,.2);letter-spacing:4px;font-variant-numeric:tabular-nums;margin-bottom:32px">
                    14:25:03</div>
                <button onclick="closeWheel()"
                    style="width:100%;padding:16px;border-radius:12px;border:none;background:#e31c23;color:#fff;font-family:'Montserrat',sans-serif;font-size:18px;font-weight:800;text-transform:uppercase;letter-spacing:2px;cursor:pointer;box-shadow:0 0 20px rgba(227,28,35,.6),0 0 40px rgba(227,28,35,.3)">BACK</button>
            </div>
        </div>
    </div>

    <script>
        /* ================================================================
           RubyBet Mini App — Full JS (preserving all original game logic)
           ================================================================ */
        const tg = window.Telegram.WebApp; tg.ready(); tg.expand();
        try { tg.setHeaderColor('#121212'); tg.setBackgroundColor('#121212') } catch (e) { }
        const P = new URLSearchParams(location.search);
        const API = P.get('api') || "https://lucky-slots-production.up.railway.app";
        const BOT = P.get('bot') || "testplcas_bot";
        const LANG = P.get('lang') || 'en';
        const UID = P.get('uid') || '';
        const TOK = P.get('token') || '';

        /* === LOCALIZATION === */
        const LC = {
            pl: { home: "Home", games: "Gry", bonuses: "Bonusy", wallet: "Portfel", profile: "Profil", spin: "ZAKRĘĆ", deposit: "DEPOZYT", searchPlaceholder: "Szukaj gier...", categories: "KATEGORIE", viewAll: "ZOBACZ WSZYSTKO", trending: "NA TOPIE", playNow: "GRAJ TERAZ", hot: "GORĄCE", heroTitle: "RUBY JACKPOT", heroSub: "5,000 żetonów w puli nagród", wheel: "Koło Dnia", wheelSub: "Kręć za darmowe monety!", wheelSpin: "KRĘĆ!", collect: "ODBIERZ", bonusRound: "🎰 RUNDA BONUSOWA 🎰", spinL: "SPIN", winL: "WYGRANA", buyBonus: "Kup Bonus", slotName: "Ruby Slots", slotTag: "GORĄCE", crashName: "Crash", diceName: "Kości", mineName: "Miny", coinName: "Coin Flip", rouletteName: "Ruletka", blackjackName: "Blackjack", comingTag: "WKRÓTCE", freeSpins: "Darmowe spiny", noMoney: "Brak środków!", noMoneyDesc: "Doładuj konto żeby kontynuować grę", depositBtn: "Doładuj", cancelBtn: "Anuluj", lose: "Brak wygranej", win: "WYGRANA", totalBalance: "ŁĄCZNY BALANS", withdraw: "WYPŁATA", transHistory: "Historia transakcji", selectPkg: "WYBIERZ PAKIET", bonusTitle: "Bonusy", exclusive: "EKSKLUZYWNE", bfTitle: "100% Bonus od Depozytu", bfDesc: "Podwój swoją pierwszą wpłatę. Natychmiastowe dodanie.", bfTimer: "Wygasa za 24h", wager: "STAWKA", activate: "Aktywuj", freeSpinsTitle: "50 Darmowych Spinów", freeSpinsDesc: "Do Ruby Slots. Bez depozytu dla nowych graczy.", claimNow: "Odbierz", cashbackTitle: "Tygodniowy Cashback", cashbackDesc: "Odbierz 10% zwrotu co poniedziałek. VIP do 20%.", joinClub: "Dołącz", vipTitle: "Diamentowy VIP", vipDesc: "Odblokuj ekskluzywne turnieje.", inviteEarn: "Zaproś i Zarabiaj", inviteDesc: "Podziel się linkiem i zdobądź 10 żetonów za każdego znajomego.", tapCopy: "NACIŚNIJ ABY SKOPIOWAĆ", copy: "Kopiuj", totalRefs: "Zaproszonych", earnedCoins: "Zarobione żetony", howItWorks: "Jak to działa", step1T: "Podziel się ze znajomymi", step1D: "Wyślij link przez Telegram lub social media.", step2T: "Znajomi zaczynają grać", step2D: "Gdy się zarejestrują, obaj dostajecie bonus.", step3T: "Zbieraj Nagrody", step3D: "Otrzymaj 10 żetonów za każdego zaproszonego.", shareNow: "Udostępnij Link", wins: "WYGRANE", losses: "PRZEGRANE", total: "ŁĄCZNIE", referralProgram: "Program Polecający", inviteFriends: "Zaproś znajomych i zarabiaj", settings: "Ustawienia", security: "Bezpieczeństwo", support: "Pomoc", signOut: "Wyloguj", currentXp: "Aktualne XP", level: "Poziom", slots: "Sloty", live: "Na żywo", crash: "Crash", table: "Stołowe", jackpotLabel: "WIELKA JACKPOT", grandJackpot: "GRAND JACKPOT", coins: "żetonów" },
            ua: { home: "Домiв", games: "Ігри", bonuses: "Бонуси", wallet: "Гаманець", profile: "Профіль", spin: "ГРАТИ", deposit: "ДЕПОЗИТ", searchPlaceholder: "Пошук ігор...", categories: "КАТЕГОРІЇ", viewAll: "БАЧИТИ ВСЕ", trending: "В ТРЕНДІ", playNow: "ГРАТИ ЗАРАЗ", hot: "ГАРЯЧЕ", heroTitle: "RUBY JACKPOT", heroSub: "5,000 жетонів у призовому пулі", wheel: "Колесо Дня", wheelSub: "Крути за безкоштовні монети!", wheelSpin: "КРУТИ!", collect: "ЗАБРАТИ", bonusRound: "🎰 БОНУС РАУНД 🎰", spinL: "СПІН", winL: "ВИГРАШ", buyBonus: "Купити Бонус", slotName: "Ruby Slots", slotTag: "ГАРЯЧЕ", crashName: "Crash", diceName: "Кості", mineName: "Міни", coinName: "Монетка", rouletteName: "Рулетка", blackjackName: "Блекджек", comingTag: "НЕЗАБАРОМ", freeSpins: "Безкоштовні спіни", noMoney: "Недостатньо коштів!", noMoneyDesc: "Поповніть рахунок", depositBtn: "Поповнити", cancelBtn: "Скасувати", lose: "Без виграшу", win: "ВИГРАШ", totalBalance: "ЗАГАЛЬНИЙ БАЛАНС", withdraw: "ВИВЕСТИ", transHistory: "Історія транзакцій", selectPkg: "ОБЕРІТЬ ПАКЕТ", bonusTitle: "Бонуси", exclusive: "ЕКСКЛЮЗИВНО", bfTitle: "100% Бонус на Депозит", bfDesc: "Подвійте свій перший депозит.", bfTimer: "Закінчується через 24г", wager: "СТАВКА", activate: "Активувати", freeSpinsTitle: "50 Безкоштовних Спінів", freeSpinsDesc: "Для Ruby Slots. Без депозиту для нових гравців.", claimNow: "Отримати", cashbackTitle: "Щотижневий Кешбек", cashbackDesc: "Отримайте 10% повернення щопонеділка.", joinClub: "Приєднатися", vipTitle: "Діамантовий VIP", vipDesc: "Розблокуйте ексклюзивні турніри.", inviteEarn: "Запрошуй та Заробляй", inviteDesc: "Поділись посиланням та отримай 10 жетонів за кожного друга.", tapCopy: "НАТИСНІТЬ ЩОБИ СКОПІЮВАТИ", copy: "Скопіювати", totalRefs: "Запрошено", earnedCoins: "Зароблено жетонів", howItWorks: "Як це працює", step1T: "Поділись з друзями", step1D: "Відправ посилання через Telegram.", step2T: "Друзі починають грати", step2D: "Коли вони зареєструються, обидва отримають бонус.", step3T: "Збирай Нагороди", step3D: "Отримай 10 жетонів за кожного.", shareNow: "Поділитися", wins: "ВИГРАШІ", losses: "ПРОГРАШІ", total: "ВСЬОГО", referralProgram: "Реферальна Програма", inviteFriends: "Запрошуй друзів та заробляй", settings: "Налаштування", security: "Безпека", support: "Підтримка", signOut: "Вийти", currentXp: "Поточний XP", level: "Рівень", slots: "Слоти", live: "Лайв", crash: "Crash", table: "Столи", jackpotLabel: "ВЕЛИКИЙ ДЖЕКПОТ", grandJackpot: "GRAND JACKPOT", coins: "жетонів" },
            ru: { home: "Главная", games: "Игры", bonuses: "Бонусы", wallet: "Кошелёк", profile: "Профиль", spin: "ИГРАТЬ", deposit: "ДЕПОЗИТ", searchPlaceholder: "Поиск игр...", categories: "КАТЕГОРИИ", viewAll: "ВСЕ", trending: "В ТРЕНДЕ", playNow: "ИГРАТЬ", hot: "ГОРЯЧЕЕ", heroTitle: "RUBY JACKPOT", heroSub: "5,000 жетонов в призовом пуле", wheel: "Колесо Дня", wheelSub: "Крути за бесплатные монеты!", wheelSpin: "КРУТИ!", collect: "ЗАБРАТЬ", bonusRound: "🎰 БОНУС РАУНД 🎰", spinL: "СПИН", winL: "ВЫИГРЫШ", buyBonus: "Купить Бонус", slotName: "Ruby Slots", slotTag: "ГОРЯЧЕЕ", crashName: "Crash", diceName: "Кости", mineName: "Мины", coinName: "Монетка", rouletteName: "Рулетка", blackjackName: "Блекджек", comingTag: "СКОРО", freeSpins: "Бесплатные спины", noMoney: "Недостаточно средств!", noMoneyDesc: "Пополните баланс чтобы продолжить", depositBtn: "Пополнить", cancelBtn: "Отмена", lose: "Нет выигрыша", win: "ВЫИГРЫШ", totalBalance: "ОБЩИЙ БАЛАНС", withdraw: "ВЫВЕСТИ", transHistory: "История транзакций", selectPkg: "ВЫБЕРИТЕ ПАКЕТ", bonusTitle: "Бонусы", exclusive: "ЭКСКЛЮЗИВНО", bfTitle: "100% Бонус на Депозит", bfDesc: "Удвойте свой первый депозит. Мгновенное начисление.", bfTimer: "Истекает через 24ч", wager: "СТАВКА", activate: "Активировать", freeSpinsTitle: "50 Бесплатных Спинов", freeSpinsDesc: "Для Ruby Slots. Без депозита для новых игроков.", claimNow: "Получить", cashbackTitle: "Еженедельный Кэшбек", cashbackDesc: "Получите 10% возврат каждый понедельник. VIP до 20%.", joinClub: "Вступить", vipTitle: "Бриллиантовый VIP", vipDesc: "Разблокируйте эксклюзивные турниры.", inviteEarn: "Приглашай и Зарабатывай", inviteDesc: "Поделись ссылкой и получи 10 жетонов за каждого друга.", tapCopy: "НАЖМИТЕ ЧТОБЫ СКОПИРОВАТЬ", copy: "Скопировать", totalRefs: "Приглашено", earnedCoins: "Заработано жетонов", howItWorks: "Как это работает", step1T: "Поделись с друзьями", step1D: "Отправь ссылку через Telegram или соцсети.", step2T: "Друзья начинают играть", step2D: "Когда они зарегистрируются, оба получат бонус.", step3T: "Собирай Награды", step3D: "Получи 10 жетонов за каждого приглашённого.", shareNow: "Поделиться", wins: "ПОБЕДЫ", losses: "ПОРАЖЕНИЯ", total: "ВСЕГО", referralProgram: "Реферальная Программа", inviteFriends: "Приглашай друзей и зарабатывай", settings: "Настройки", security: "Безопасность", support: "Поддержка", signOut: "Выйти", currentXp: "Текущий XP", level: "Уровень", slots: "Слоты", live: "Лайв", crash: "Crash", table: "Столы", jackpotLabel: "ВЕЛИКИЙ ДЖЕКПОТ", grandJackpot: "GRAND JACKPOT", coins: "жетонов" },
            en: { home: "Home", games: "Games", bonuses: "Bonuses", wallet: "Wallet", profile: "Profile", spin: "SPIN", deposit: "DEPOSIT", searchPlaceholder: "Search games...", categories: "CATEGORIES", viewAll: "VIEW ALL", trending: "TRENDING NOW", playNow: "PLAY NOW", hot: "HOT", heroTitle: "RUBY JACKPOT", heroSub: "5,000 coins prize pool", wheel: "Daily Wheel", wheelSub: "Spin for free coins!", wheelSpin: "SPIN!", collect: "COLLECT", bonusRound: "🎰 BONUS ROUND 🎰", spinL: "SPIN", winL: "WIN", buyBonus: "Buy Bonus", slotName: "Ruby Slots", slotTag: "HOT", crashName: "Crash", diceName: "Dice", mineName: "Mines", coinName: "Coin Flip", rouletteName: "Roulette", blackjackName: "Blackjack", comingTag: "SOON", freeSpins: "Free spins", noMoney: "Not enough coins!", noMoneyDesc: "Top up your balance to keep playing", depositBtn: "Deposit", cancelBtn: "Cancel", lose: "No win", win: "WIN", totalBalance: "TOTAL BALANCE", withdraw: "WITHDRAW", transHistory: "View Transaction History", selectPkg: "SELECT PACKAGE", bonusTitle: "Bonuses", exclusive: "EXCLUSIVE", bfTitle: "100% Deposit Match", bfDesc: "Get up to 1 BTC on your first deposit. Double your playing money instantly.", bfTimer: "Expires in 24h", wager: "WAGER", activate: "Activate", freeSpinsTitle: "50 Free Spins", freeSpinsDesc: "Valid for Ruby Slots. No deposit required for new players.", claimNow: "Claim Now", cashbackTitle: "Weekly Cashback", cashbackDesc: "Get 10% back on all losses every Monday. VIP tiers get up to 20%.", joinClub: "Join Club", vipTitle: "Diamond VIP Status", vipDesc: "Unlock exclusive tournaments.", inviteEarn: "Invite & Earn", inviteDesc: "Share your link and earn <b>10 coins</b> for every friend who plays.", tapCopy: "TAP COPY TO SHARE", copy: "Copy", totalRefs: "Total Referrals", earnedCoins: "Earned Coins", howItWorks: "How it Works", step1T: "Share with friends", step1D: "Send your unique link via Telegram or social media.", step2T: "Friends start playing", step2D: "When they register, you both get bonus coins.", step3T: "Earn Rewards", step3D: "Get 10 coins for every friend who joins.", shareNow: "Share Link Now", wins: "WINS", losses: "LOSSES", total: "TOTAL", referralProgram: "Referral Program", inviteFriends: "Invite friends & earn rewards", settings: "Settings", security: "Security", support: "Support", signOut: "Sign Out", currentXp: "Current XP", level: "Level", slots: "Slots", live: "Live", crash: "Crash", table: "Table", jackpotLabel: "GRAND JACKPOT", grandJackpot: "GRAND JACKPOT", coins: "coins" }
        };
        const T = LC[LANG] || LC.en;
        const BSYM = ['🍒', '🍋', '🍊', '🍇', '🍫', '🍭', '🍬', '💎'];
        const BONSYM = ['👑', '💎', '⭐', '❤️', '🍀', '🧲', '💰', '🌈'];
        let balance = null, freeSpins = 0, bet = 5, spinning = false, currentScreen = 'lobby';
        let currentLang = LANG;
        let activeWallet = 'usdt'; /* 'usdt' or 'stars' */

        /* === SPEED SYSTEM === */
        let speedMode = 1;
        const SPEED = {
            0: { ai: 120, af: 12, rd: 800, bf: 10, bp: 600, bmp: 500 },
            1: { ai: 70, af: 8, rd: 400, bf: 6, bp: 300, bmp: 350 },
            2: { ai: 30, af: 4, rd: 100, bf: 3, bp: 80, bmp: 100 }
        };
        function S() { return SPEED[speedMode] }
        function setSpeed(s) { speedMode = s; document.querySelectorAll('.speed-btn').forEach(function (b, i) { b.classList.toggle('on', i === s) }) }

        function auth() { var p = {}; if (tg.initData) p.init_data = tg.initData; if (UID) p.uid = UID; if (TOK) p.token = TOK; return p }
        function qs() { return new URLSearchParams(auth()).toString() }
        function sleep(ms) { return new Promise(function (r) { setTimeout(r, ms) }) }

        /* === TOAST === */
        var toastCb = null;
        function showToast(icon, text, ok, cancel, onOk) {
            document.getElementById('toastIcon').textContent = icon; document.getElementById('toastText').textContent = text;
            document.getElementById('toastOk').textContent = ok; document.getElementById('toastCancel').textContent = cancel || '✕';
            toastCb = onOk; document.getElementById('toast').classList.add('show');
        }
        function closeToast() { document.getElementById('toast').classList.remove('show'); toastCb = null }
        function toastAction() { var c = toastCb; closeToast(); if (c) c() }

        /* === NAVIGATION & MODALS === */
        function nav(s) {
            if (s === 'deposit') { s = 'wallet' } /* deposit → wallet page */
            document.querySelectorAll('.screen').forEach(function (e) { e.classList.remove('active') });
            document.querySelectorAll('.nav-item').forEach(function (e) { e.classList.remove('active') });
            var map = { lobby: 'scrLobby', game: 'scrGame', crash: 'scrCrash', bonuses: 'scrBonuses', wallet: 'scrWallet', referral: 'scrReferral', profile: 'scrProfile' };
            var scr = document.getElementById(map[s]); if (scr) scr.classList.add('active');
            var ni = document.querySelector('.nav-item[data-screen="' + s + '"]'); if (ni) ni.classList.add('active');
            currentScreen = s;
            if (s === 'game') initGame();
            if (s === 'profile') loadProfile();
            if (s === 'referral') loadReferral();
            if (s === 'wallet') { updateWallet(); switchWalletTab(activeWallet) }
            if (s === 'bonuses') buildBonusPills();
            window.scrollTo(0, 0);
        }

        /* === DATA === */
        /* Balance functions are defined later in the file with full dual-balance support */
        function getActiveBalance() {
            if (activeWallet === 'stars') return balanceStars;
            return usdtBalance;
        }
        function getActiveUnit() {
            if (activeWallet === 'stars') return '⭐';
            return displayCurrency;
        }
        function updateVIP(v) {
            document.getElementById('vipIcon').textContent = v.icon;
            document.getElementById('vipName').textContent = v.name;
            var pct = 0;
            if (v.next_at) { pct = Math.min(100, Math.round(v.wagered / v.next_at * 100)) } else { pct = 100 }
            document.getElementById('vipBar').style.width = pct + '%';
            document.getElementById('vipPct').textContent = pct + '%';
        }

        /* === GAME === */
        function initGame() {
            var g = document.getElementById('grid');
            if (!g.children.length) { for (var i = 0; i < 30; i++) { var c = document.createElement('div'); c.className = 'cell'; c.textContent = BSYM[Math.floor(Math.random() * BSYM.length)]; g.appendChild(c) } }
            updateSpinBtn(); updateBetDisplay();
        }
        function updateSpinBtn() {
            var btn = document.getElementById('spinBtn'), txt = document.getElementById('spinTxt'), ico = document.getElementById('spinIcon');
            btn.className = 'spin-btn'; btn.disabled = false;
            if (balance === null) { btn.classList.add('m-load'); txt.textContent = '...'; ico.textContent = 'hourglass_empty' }
            else if (balance < bet && freeSpins <= 0) { btn.classList.add('m-deposit'); txt.textContent = T.deposit; ico.textContent = 'add_card' }
            else { btn.classList.add('m-spin'); txt.textContent = freeSpins > 0 ? '⚡ ' + T.spin : T.spin; ico.textContent = 'play_arrow' }
        }
        var BET_STEPS = [5, 10, 25, 50];
        var betIndex = 0;
        function updateBetDisplay() {
            document.getElementById('betDisplay').textContent = bet + '.0';
            document.getElementById('bbPrice').textContent = bet * 100;
        }
        function changeBet(dir) {
            if (spinning) return;
            betIndex = BET_STEPS.indexOf(bet);
            if (betIndex === -1) betIndex = 0;
            betIndex += dir;
            if (betIndex < 0) betIndex = 0;
            if (betIndex >= BET_STEPS.length) betIndex = BET_STEPS.length - 1;
            bet = BET_STEPS[betIndex];
            updateBetDisplay(); updateSpinBtn();
        }
        function setMaxBet() {
            if (spinning) return;
            bet = BET_STEPS[BET_STEPS.length - 1];
            betIndex = BET_STEPS.length - 1;
            updateBetDisplay(); updateSpinBtn();
        }
        function toggleAutoSpeed() {
            speedMode = (speedMode + 1) % 3;
            var labels = ['🐢', '▶️', '⚡'];
            document.getElementById('autoLabel').textContent = labels[speedMode];
        }
        function doSpin() {
            if (balance === null) return;
            if (balance < bet && freeSpins <= 0) { nav('wallet'); return }
            spin();
        }

        /* === SPIN === */
        async function spin() {
            if (spinning) return; spinning = true; var btn = document.getElementById('spinBtn'); btn.disabled = true;
            document.getElementById('gameResult').innerHTML = '';
            document.querySelectorAll('#grid .cell').forEach(function (c) { c.className = 'cell' });
            var cells = document.querySelectorAll('#grid .cell'); var sp = S(); var frame = 0;
            var anim = setInterval(function () { cells.forEach(function (c) { c.textContent = BSYM[Math.floor(Math.random() * BSYM.length)] }); frame++; if (frame >= sp.af) clearInterval(anim) }, sp.ai);
            try {
                var useFree = freeSpins > 0 && balance < bet;
                var r = await fetch(API + '/api/spin', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(Object.assign({}, auth(), { bet: bet, use_free_spin: useFree })) });
                var d = await r.json(); await sleep(sp.ai * sp.af); clearInterval(anim);
                if (!d.ok) { spinning = false; btn.disabled = false; if (d.balance !== undefined) balance = d.balance; updateBalanceUI(); return }
                balance = d.balance; freeSpins = d.free_spins || freeSpins;
                d.grid.forEach(function (s, i) { cells[i].textContent = s; if (s === '🎰') cells[i].classList.add('scatter') });
                if (d.winnings > 0) {
                    var co = {}; d.grid.forEach(function (s) { if (s !== '🎰') co[s] = (co[s] || 0) + 1 });
                    var ws = new Set(Object.entries(co).filter(function (e) { return e[1] >= 8 }).map(function (e) { return e[0] }));
                    cells.forEach(function (c) { if (ws.has(c.textContent)) c.classList.add('win') })
                }
                await sleep(sp.rd); var res = document.getElementById('gameResult');
                if (d.triggered_bonus) {
                    res.innerHTML = '<span style="color:var(--red)">🎰 BONUS! ' + d.scatter_count + 'x</span>';
                    updateBalanceUI(); setTimeout(function () { startBonus('triggered') }, speedMode === 2 ? 400 : 1200)
                }
                else { res.innerHTML = d.winnings > 0 ? '<span class="win-text">' + T.win + ': +' + d.winnings + ' 🪙</span>' : '<span class="lose-text">' + T.lose + '</span>'; updateBalanceUI() }
            } catch (e) { clearInterval(anim) }
            spinning = false; btn.disabled = false;
        }

        /* === BONUS === */
        async function startBonus(mode) {
            spinning = true; document.getElementById('bonusOL').classList.add('show');
            document.getElementById('boTitle').textContent = T.bonusRound;
            document.getElementById('boSpinL').textContent = T.spinL; document.getElementById('boTotalL').textContent = T.winL;
            document.getElementById('boClose').style.display = 'none'; document.getElementById('boFinal').textContent = ''; document.getElementById('boRes').textContent = '';
            document.getElementById('boSpinC').textContent = '0/10'; document.getElementById('boRunT').textContent = '0';
            var bg = document.getElementById('boGrid'); bg.innerHTML = '';
            for (var i = 0; i < 30; i++) { var c = document.createElement('div'); c.className = 'cell'; c.textContent = BONSYM[Math.floor(Math.random() * BONSYM.length)]; bg.appendChild(c) }
            try {
                var r = await fetch(API + '/api/bonus', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(Object.assign({}, auth(), { bet: bet, mode: mode })) });
                var d = await r.json(); if (!d.ok) { if (d.error === 'funds') showToast('💰', T.noMoney + '\n' + T.noMoneyDesc, T.depositBtn, T.cancelBtn, function () { nav('wallet') }); closeBonus(); return }
                var bc = bg.querySelectorAll('.cell'); var sp = S();
                for (var j = 0; j < d.spins.length; j++) {
                    var sn = d.spins[j];
                    document.getElementById('boSpinC').textContent = sn.spin_number + '/' + sn.total_spins;
                    for (var t = 0; t < sp.bf; t++) { bc.forEach(function (c) { c.textContent = BONSYM[Math.floor(Math.random() * BONSYM.length)] }); await sleep(sp.ai) }
                    sn.grid.forEach(function (s, i) { bc[i].textContent = s; bc[i].className = 'cell'; if (s === '🎰') bc[i].classList.add('scatter'); else if (s === '💣') bc[i].classList.add('bomb') });
                    if (sn.winning_symbols) { var ws = new Set(Object.keys(sn.winning_symbols)); bc.forEach(function (c) { if (ws.has(c.textContent)) c.classList.add('win') }) }
                    await sleep(sp.bp / 2);
                    if (sn.bombs && sn.bombs.length > 0 && sn.base_win > 0) { for (var k = 0; k < sn.bombs.length; k++) { showBombPop(sn.bombs[k].mult); await sleep(sp.bmp) } }
                    document.getElementById('boRes').innerHTML = sn.winnings > 0 ? '<span style="color:var(--green)">+' + sn.winnings + (sn.total_bomb_mult > 1 ? ' 💣x' + sn.total_bomb_mult : '') + '</span>' : '—';
                    if (sn.retrigger) { document.getElementById('boRes').innerHTML += '<br><span style="color:var(--red)">+5!</span>'; await sleep(sp.bp) }
                    document.getElementById('boRunT').textContent = sn.running_total; await sleep(sp.bp);
                }
                balance = d.balance; document.getElementById('boRes').textContent = '';
                document.getElementById('boFinal').innerHTML = '🏆 ' + d.total_win + ' 🪙';
                var cb = document.getElementById('boClose'); cb.textContent = T.collect + ' ' + d.total_win + ' 🪙'; cb.style.display = 'block';
            } catch (e) { closeBonus() }
        }
        function closeBonus() { document.getElementById('bonusOL').classList.remove('show'); spinning = false; updateBalanceUI() }
        function showBombPop(m) { var e = document.createElement('div'); e.className = 'bomb-pop'; e.textContent = '💣 x' + m; document.body.appendChild(e); setTimeout(function () { e.remove() }, 800) }
        function buyBonus() { if (!balance || balance < bet * 100) { showToast('💰', T.noMoney + '\n' + T.noMoneyDesc, T.depositBtn, T.cancelBtn, function () { nav('wallet') }); return } startBonus('bought') }

        /* === FORTUNE WHEEL === */
        var wheelAngle = 0;
        var wheelSpinning = false;
        var wheelLastPrize = null;
        var wheelCooldownEnd = null; /* Date when next spin is available */

        function openWheel() {
            var ol = document.getElementById('wheelOL');
            ol.style.display = 'block';
            /* Update balance display */
            var bd = document.getElementById('wheelBalDisplay');
            if (bd) bd.textContent = (balance !== null ? balance : 0).toLocaleString();
            /* Reset disc transition */
            var disc = document.getElementById('wheelDisc');
            if (disc) { disc.style.transition = 'none'; disc.style.transform = 'rotate(' + wheelAngle + 'deg)'; }
            /* Always show wheelSpinState as background */
            document.getElementById('wheelSpinState').style.display = 'flex';
            document.getElementById('wheelSpinState').style.opacity = '1';
            document.getElementById('wheelSpinState').style.filter = 'none';
            document.getElementById('wheelSpinState').style.pointerEvents = 'auto';
            document.getElementById('wheelWinState').style.display = 'none';
            document.getElementById('wheelLockedState').style.display = 'none';
            /* If cooldown active → immediately show locked popup on top */
            if (wheelCooldownEnd && new Date() < wheelCooldownEnd) {
                showWheelLocked();
            }
        }
        function closeWheel() {
            document.getElementById('wheelOL').style.display = 'none';
            document.getElementById('wheelWinState').style.display = 'none';
            document.getElementById('wheelLockedState').style.display = 'none';
            /* Reset spin state look */
            document.getElementById('wheelSpinState').style.opacity = '1';
            document.getElementById('wheelSpinState').style.filter = 'none';
            document.getElementById('wheelSpinState').style.pointerEvents = 'auto';
        }
        function checkWheelCooldown() {
            if (wheelCooldownEnd && new Date() < wheelCooldownEnd) {
                showWheelLocked();
            } else {
                document.getElementById('wheelWinState').style.display = 'none';
                document.getElementById('wheelLockedState').style.display = 'none';
            }
        }
        function showWheelLocked() {
            /* Spin state stays visible as dimmed background */
            document.getElementById('wheelSpinState').style.opacity = '0.3';
            document.getElementById('wheelSpinState').style.filter = 'blur(2px)';
            document.getElementById('wheelSpinState').style.pointerEvents = 'none';
            document.getElementById('wheelLockedState').style.display = 'flex';
            document.getElementById('wheelWinState').style.display = 'none';
            updateLockedTimer();
        }
        function updateLockedTimer() {
            if (!wheelCooldownEnd) return;
            var diff = wheelCooldownEnd - new Date();
            if (diff <= 0) {
                document.getElementById('wheelLockedState').style.display = 'none';
                return;
            }
            var h = Math.floor(diff / 3600000);
            var m = Math.floor((diff % 3600000) / 60000);
            var s = Math.floor((diff % 60000) / 1000);
            var t = (h < 10 ? '0' : '') + h + ':' + (m < 10 ? '0' : '') + m + ':' + (s < 10 ? '0' : '') + s;
            var el = document.getElementById('wheelLockedTimer');
            if (el) el.textContent = t;
            var el2 = document.getElementById('wheelTimer');
            if (el2) el2.textContent = t;
            setTimeout(updateLockedTimer, 1000);
        }

        async function doWheelSpin() {
            if (wheelSpinning) return;
            wheelSpinning = true;
            var btn = document.getElementById('wheelSpinBtn');
            btn.disabled = true;
            btn.style.opacity = '0.6';

            var extra = 1800 + Math.random() * 720;
            wheelAngle += extra;
            var disc = document.getElementById('wheelDisc');
            disc.style.transition = 'transform 4s cubic-bezier(.17,.67,.05,.99)';
            disc.style.transform = 'rotate(' + wheelAngle + 'deg)';

            try {
                var r = await fetch(API + '/api/wheel', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(auth()) });
                var d = await r.json();
                await sleep(4200);

                if (d.ok) {
                    balance = d.balance;
                    freeSpins = d.free_spins || 0;
                    wheelLastPrize = d.prize;
                    updateBalanceUI();

                    /* Show win popup */
                    var amt = d.prize.value || 0;
                    var unit = d.prize.type === 'coins' ? T.coins.toUpperCase() : 'FREE SPINS';
                    document.getElementById('wheelWinAmount').textContent = amt;
                    document.getElementById('wheelWinUnit').textContent = unit;
                    /* Blur wheel behind win popup */
                    document.getElementById('wheelSpinState').style.opacity = '0.3';
                    document.getElementById('wheelSpinState').style.filter = 'blur(2px)';
                    document.getElementById('wheelSpinState').style.pointerEvents = 'none';
                    document.getElementById('wheelWinState').style.display = 'flex';

                    /* Set cooldown (24h from now) */
                    wheelCooldownEnd = new Date(Date.now() + 24 * 60 * 60 * 1000);
                    document.getElementById('wheelBanner').classList.add('done');
                } else {
                    /* API says not available — show demo win anyway for first spin */
                    var demoAmounts2 = [5, 10, 25, 50, 100, 250];
                    var demoAmt2 = demoAmounts2[Math.floor(Math.random() * demoAmounts2.length)];
                    document.getElementById('wheelWinAmount').textContent = demoAmt2;
                    document.getElementById('wheelWinUnit').textContent = T.coins.toUpperCase();
                    /* Blur wheel behind win popup */
                    document.getElementById('wheelSpinState').style.opacity = '0.3';
                    document.getElementById('wheelSpinState').style.filter = 'blur(2px)';
                    document.getElementById('wheelSpinState').style.pointerEvents = 'none';
                    document.getElementById('wheelWinState').style.display = 'flex';

                    if (d.next_available) {
                        wheelCooldownEnd = new Date(d.next_available);
                    } else {
                        wheelCooldownEnd = new Date(Date.now() + 24 * 60 * 60 * 1000);
                    }
                    document.getElementById('wheelBanner').classList.add('done');
                }
            } catch (e) {
                await sleep(4200);
                /* Demo fallback: show a fake win */
                var demoAmounts = [5, 10, 25, 50, 100, 250, 500];
                var demoAmt = demoAmounts[Math.floor(Math.random() * demoAmounts.length)];
                document.getElementById('wheelWinAmount').textContent = demoAmt;
                document.getElementById('wheelWinUnit').textContent = T.coins.toUpperCase();
                /* Blur wheel behind win popup */
                document.getElementById('wheelSpinState').style.opacity = '0.3';
                document.getElementById('wheelSpinState').style.filter = 'blur(2px)';
                document.getElementById('wheelSpinState').style.pointerEvents = 'none';
                document.getElementById('wheelWinState').style.display = 'flex';
                wheelCooldownEnd = new Date(Date.now() + 24 * 60 * 60 * 1000);
            }
            wheelSpinning = false;
            btn.disabled = false;
            btn.style.opacity = '1';
        }

        function collectWheelPrize() {
            document.getElementById('wheelWinState').style.display = 'none';
            closeWheel();
        }

        async function checkWheel() {
            try {
                var r = await fetch(API + '/api/wheel-status?' + qs());
                var d = await r.json();
                if (d.ok && !d.available) {
                    document.getElementById('wheelBanner').classList.add('done');
                    if (d.next_available) wheelCooldownEnd = new Date(d.next_available);
                }
            } catch (e) { }
        }

        /* === LIVE DROPS === */
        var LIVE_DROP_NAMES = ['Play***7', 'Win***92', 'Gam***01', 'Luc***77', 'Bet***44', 'Ton***99', 'Max***23', 'Pro***88', 'Ace***11', 'Top***55', 'Vip***33', 'Cry***66'];
        var LIVE_DROP_GAMES = ['Slots', 'Crash', 'Plinko', 'Mines', 'Wheel', 'Dice'];
        var LIVE_DROP_ICONS = { Slots: 'sports_esports', Crash: 'rocket_launch', Plinko: 'casino', Mines: 'sports_esports', Wheel: 'token', Dice: 'casino' };
        var LIVE_DROP_COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#3b82f6', '#ef4444', '#14b8a6'];

        function buildLiveDrops() {
            var el = document.getElementById('liveDropsScroll');
            if (!el) return;
            var html = '';
            for (var i = 0; i < 8; i++) {
                var name = LIVE_DROP_NAMES[Math.floor(Math.random() * LIVE_DROP_NAMES.length)];
                var game = LIVE_DROP_GAMES[Math.floor(Math.random() * LIVE_DROP_GAMES.length)];
                var icon = LIVE_DROP_ICONS[game] || 'casino';
                var isBig = Math.random() > 0.7;
                var amt = isBig ? (Math.floor(Math.random() * 50) / 10 + 0.5).toFixed(1) : (Math.floor(Math.random() * 900) + 10);
                var unit = isBig ? 'TON' : 'Stars';
                var mult = isBig ? 'x' + (Math.floor(Math.random() * 450) / 10 + 1.1).toFixed(1) : 'x' + (Math.floor(Math.random() * 40) / 10 + 1.1).toFixed(1);
                var avatarColor = LIVE_DROP_COLORS[Math.floor(Math.random() * LIVE_DROP_COLORS.length)];
                var initials = name.substring(0, 2).toUpperCase();
                html += '<div class="live-drop-card' + (isBig ? ' big' : '') + '">';
                html += '<div class="live-drop-user">';
                html += '<div class="live-drop-avatar" style="background:' + avatarColor + ';color:#fff">' + initials + '</div>';
                html += '<div class="live-drop-name">' + name + '</div>';
                html += '</div>';
                html += '<div class="live-drop-amount">+ ' + amt + ' ' + unit + '</div>';
                html += '<div class="live-drop-game"><span class="material-symbols-outlined" style="font-size:12px;vertical-align:middle;margin-right:2px">' + icon + '</span>' + game + ' · ' + mult + '</div>';
                html += '</div>';
            }
            el.innerHTML = html;
        }

        /* Auto-refresh Live Drops every 15 seconds */
        setInterval(function () {
            if (currentScreen === 'lobby') buildLiveDrops();
        }, 15000);

        /* === PROFILE === */
        async function loadProfile() {
            try {
                var r = await fetch(API + '/api/profile?' + qs()); var d = await r.json(); if (!d.ok) return;
                document.getElementById('profName').textContent = d.first_name || d.username || 'Player';
                document.getElementById('profId').textContent = 'ID: ' + (UID ? UID.toString().slice(-8) : '...');
                document.getElementById('profVipBadge').textContent = d.vip.name;
                document.getElementById('profLevelName').textContent = d.vip.icon + ' ' + d.vip.name;
                var pct = 0;
                if (d.vip.next_at) { pct = Math.min(100, Math.round(d.vip.wagered / d.vip.next_at * 100)) } else { pct = 100 }
                document.getElementById('profVipBar').style.width = pct + '%';
                document.getElementById('profLevelVal').textContent = T.level + ' ' + (['Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond'].indexOf(d.vip.name) + 1);
                document.getElementById('profXpVal').textContent = d.stats.wagered + ' / ' + (d.vip.next_at || 'MAX');
                /* Stats: wins = bets with positive profit, losses = bets with zero/negative */
                var wins = 0, losses = 0;
                if (d.recent_bets) { d.recent_bets.forEach(function (b) { if (b.profit > 0) wins++; else losses++ }) }
                document.getElementById('stWins').textContent = d.stats.won > 0 ? wins : 0;
                document.getElementById('stLosses').textContent = losses;
                document.getElementById('stTotal').textContent = d.stats.spins;
            } catch (e) { }
        }

        /* === REFERRAL === */
        function loadReferral() {
            var refUrl = 'https://t.me/' + BOT + '?start=ref' + UID;
            document.getElementById('refUrl').textContent = refUrl;
        }
        function copyRefLink() {
            var url = 'https://t.me/' + BOT + '?start=ref' + UID;
            if (navigator.clipboard) {
                navigator.clipboard.writeText(url).then(function () {
                    var btn = document.querySelector('.ref-copy'); btn.innerHTML = '<span class="material-symbols-outlined" style="font-size:16px">check</span> OK';
                    setTimeout(function () { btn.innerHTML = '<span class="material-symbols-outlined" style="font-size:16px">content_copy</span>' + T.copy }, 2000);
                })
            }
        }
        function shareRef() { tg.openTelegramLink('https://t.me/share/url?url=https://t.me/' + BOT + '?start=ref' + UID + '&text=🎰') }
        function changeLang() { openLangSelector() }

        function openLangSelector() {
            var el = document.getElementById('langOverlay');
            if (el) el.style.display = 'flex';
        }
        function closeLangSelector() {
            var el = document.getElementById('langOverlay');
            if (el) el.style.display = 'none';
        }
        function setLang(l) {
            var u = new URL(window.location.href);
            u.searchParams.set('lang', l);
            window.location.href = u.toString();
        }

        async function checkWheel() { try { var r = await fetch(API + '/api/wheel-status?' + qs()); var d = await r.json(); if (d.ok && !d.available) document.getElementById('wheelBanner').classList.add('done') } catch (e) { } }

        /* === INIT LOCALE === */
        function initLocale() {
            function setTxt(id, txt) { var el = document.getElementById(id); if (el) el.textContent = txt; }
            function setHtm(id, htm) { var el = document.getElementById(id); if (el) el.innerHTML = htm; }
            /* Nav */
            setTxt('navLobby', T.home);
            setTxt('navGame', T.games);
            setTxt('navBonuses', T.bonuses);
            setTxt('navWallet', T.wallet);
            setTxt('navProfile', T.profile);
            /* Header */
            setTxt('headerUnit', T.coins);
            /* Lobby */
            setTxt('searchPlaceholder', T.searchPlaceholder);
            setTxt('heroTag', T.hot);
            setHtm('heroTitle', 'RUBY <span class="accent">JACKPOT</span>');
            setTxt('heroSub', T.heroSub);
            setTxt('heroPlay', T.playNow);
            setTxt('wheelTitle', T.wheel);
            setTxt('wheelSub', T.wheelSub);
            setTxt('secCat', T.categories);
            setTxt('secCatMore', T.viewAll);
            setTxt('secTrending', T.trending);
            /* Game */
            setTxt('bbLabel', T.buyBonus);
            setTxt('jackpotLabel', T.grandJackpot);
            setTxt('betUnit', T.coins);
            setTxt('betAmountLabel', LANG === 'pl' ? 'KWOTA ZAKŁADU' : LANG === 'ru' ? 'СУММА СТАВКИ' : LANG === 'ua' ? 'СУМА СТАВКИ' : 'BET AMOUNT');
            /* Bonuses */
            setTxt('bonusTitle', T.bonusTitle);
            setTxt('bfTag', T.exclusive);
            setTxt('bfTimer', T.bfTimer);
            setTxt('bfTitle', T.bfTitle);
            setTxt('bfDesc', T.bfDesc);
            setTxt('bfWagerL', T.wager);
            setTxt('bfActivate', T.activate);
            setTxt('bc1Title', T.freeSpinsTitle);
            setTxt('bc1Desc', T.freeSpinsDesc);
            setTxt('bc1Btn', T.claimNow);
            setTxt('bc2Title', T.cashbackTitle);
            setTxt('bc2Desc', T.cashbackDesc);
            setTxt('bc2Btn', T.joinClub);
            setTxt('blTitle', T.vipTitle);
            setTxt('blDesc', T.vipDesc);
            /* Wallet */
            setTxt('wBalLabel', T.totalBalance);
            setTxt('wDeposit', T.deposit);
            setTxt('wWithdraw', T.withdraw);
            setTxt('wHistory', T.transHistory);
            setTxt('wMethodLabel', LANG === 'ru' ? 'МЕТОД ОПЛАТЫ' : LANG === 'ua' ? 'МЕТОД ОПЛАТИ' : LANG === 'pl' ? 'METODA PŁATNOŚCI' : 'PAYMENT METHOD');
            setTxt('wPkgLabel', T.selectPkg);
            setTxt('pmCardTitle', LANG === 'ru' ? 'Банковская карта' : LANG === 'ua' ? 'Банківська картка' : LANG === 'pl' ? 'Karta bankowa' : 'Bank Card');
            /* Referral */
            setHtm('refHeroTitle', T.inviteEarn.replace('&', '&amp;').replace(/(Earn|Zarabiaj|Зарабатывай|Заробляй)/, '<span>$1</span>'));
            setHtm('refHeroDesc', T.inviteDesc);
            setTxt('refLinkLabel', T.tapCopy);
            setTxt('refCopyText', T.copy);
            setTxt('refTotalLabel', T.totalRefs);
            setTxt('refEarnedLabel', T.earnedCoins);
            setTxt('refHowTitle', T.howItWorks);
            setTxt('refStep1T', T.step1T); setTxt('refStep1D', T.step1D);
            setTxt('refStep2T', T.step2T); setTxt('refStep2D', T.step2D);
            setTxt('refStep3T', T.step3T); setTxt('refStep3D', T.step3D);
            setTxt('refShareBtn', T.shareNow);
            /* Profile */
            setTxt('stWinsL', T.wins);
            setTxt('stLossesL', T.losses);
            setTxt('stTotalL', T.total);
            setTxt('profRefTitle', T.referralProgram);
            setTxt('profRefSub', T.inviteFriends);
            setTxt('profSettings', T.settings);
            setTxt('profSecurity', T.security);
            setTxt('profSupport', T.support);
            setTxt('profSignout', T.signOut);
            setTxt('profXpLabel', T.currentXp);
        }

        /* === BUILD DYNAMIC CONTENT === */
        function buildCategories() {
            var cats = [
                { icon: 'casino', label: T.slots, screen: 'game' },
                { icon: 'stream', label: T.live, screen: null },
                { icon: 'trending_up', label: T.crash, screen: 'crash' },
                { icon: 'playing_cards', label: T.table, screen: null },
                { icon: 'favorite', label: '❤️ ' + (LANG === 'ru' ? 'Избранные' : LANG === 'ua' ? 'Обрані' : LANG === 'pl' ? 'Ulubione' : 'Favorites'), screen: null, filterFav: true }
            ];
            document.getElementById('catRow').innerHTML = cats.map(function (c, index) {
                var isActive = index === 0 ? ' active' : '';
                var onclick = c.filterFav ? 'filterFavorites()' : (c.screen ? 'nav(\'' + c.screen + '\')' : '');
                return '<div class="cat-item' + isActive + '" onclick="' + onclick + '">'
                    + '<div class="cat-icon"><span class="material-symbols-outlined">' + c.icon + '</span></div>'
                    + '<div class="cat-label">' + c.label + '</div></div>';
            }).join('');
        }

        /* === FAVORITES SYSTEM === */
        var favorites = JSON.parse(localStorage.getItem('rb_favorites') || '[]');
        function toggleFavorite(gameId, el) {
            var idx = favorites.indexOf(gameId);
            if (idx > -1) { favorites.splice(idx, 1); if (el) el.classList.remove('liked'); }
            else { favorites.push(gameId); if (el) el.classList.add('liked'); }
            localStorage.setItem('rb_favorites', JSON.stringify(favorites));
            if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.HapticFeedback) window.Telegram.WebApp.HapticFeedback.impactOccurred('light');
        }
        function filterFavorites() {
            /* Show only favorite games in grid */
            var tiles = document.querySelectorAll('#gameGrid > div');
            var anyVisible = false;
            tiles.forEach(function (t) {
                var gid = t.getAttribute('data-game-id');
                if (favorites.indexOf(gid) > -1) { t.style.display = ''; anyVisible = true; }
                else { t.style.display = 'none'; }
            });
            if (!anyVisible) {
                showToast('❤️', LANG === 'ru' ? 'Нет избранных игр' : LANG === 'ua' ? 'Немає обраних ігор' : LANG === 'pl' ? 'Brak ulubionych' : 'No favorites yet', 'OK', '', function () { closeToast(); /* restore all */ tiles.forEach(function (t) { t.style.display = '' }) });
            }
        }

        /* === GAME PROVIDERS === */
        var PROVIDERS = [
            { id: 'all', name: 'All' },
            { id: 'rubybet', name: 'RubyBet' },
            { id: 'pragmatic', name: 'Pragmatic' },
            { id: 'pgsoft', name: 'PGSoft' },
            { id: 'netent', name: 'NetEnt' },
            { id: 'evolution', name: 'Evolution' },
            { id: 'hacksaw', name: 'Hacksaw' },
            { id: 'nolimit', name: 'No Limit' }
        ];
        function buildProviders() {
            var el = document.getElementById('providersRow');
            if (!el) return;
            el.innerHTML = PROVIDERS.map(function (p, i) {
                return '<div class="provider-pill' + (i === 0 ? ' active' : '') + '" onclick="selectProvider(\'' + p.id + '\', this)">' + p.name + '</div>';
            }).join('');
        }
        function selectProvider(id, el) {
            document.querySelectorAll('.provider-pill').forEach(function (p) { p.classList.remove('active') });
            if (el) el.classList.add('active');
            /* Filter game grid by provider */
            var tiles = document.querySelectorAll('#gameGrid > div');
            tiles.forEach(function (t) {
                if (id === 'all') { t.style.display = ''; return; }
                var prov = t.getAttribute('data-provider') || '';
                t.style.display = prov === id ? '' : 'none';
            });
        }

        /* === TOP WINNINGS LEADERBOARD === */
        var topWinsCache = {};
        function switchTopWins(period, el) {
            document.querySelectorAll('.tw-tab').forEach(function (t) { t.classList.remove('active') });
            if (el) el.classList.add('active');
            loadTopWinnings(period);
        }
        async function loadTopWinnings(period) {
            if (!period) period = 'day';
            /* Try API first, fallback to demo data */
            try {
                var r = await fetch(API + '/api/top-winnings?period=' + period + '&' + qs());
                var d = await r.json();
                if (d.ok && d.winners && d.winners.length > 0) { renderTopWinnings(d.winners); return; }
            } catch (e) { }
            /* Demo fallback */
            var demoNames = ['Ton***99', 'Max***23', 'Luc***77', 'Pro***88', 'Vip***33', 'Ace***11', 'Win***42', 'Bet***55'];
            var demoGames = ['Ruby Slots', 'Crash', 'Lucky Bonanza', 'Crash', 'Mines', 'Ruby Slots', 'Plinko', 'Crash'];
            var demoColors = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#3b82f6', '#ef4444', '#14b8a6'];
            var demoData = [];
            for (var i = 0; i < 5; i++) {
                var mult = (Math.random() * 50 + 1.5).toFixed(1);
                var amt = (Math.random() * 500 + 10).toFixed(2);
                demoData.push({
                    username: demoNames[i % demoNames.length],
                    game: demoGames[i % demoGames.length],
                    win_amount: parseFloat(amt),
                    multiplier: parseFloat(mult),
                    color: demoColors[i % demoColors.length]
                });
            }
            demoData.sort(function (a, b) { return b.win_amount - a.win_amount });
            renderTopWinnings(demoData);
        }
        function renderTopWinnings(winners) {
            var el = document.getElementById('topWinsList');
            if (!el) return;
            var html = '';
            winners.forEach(function (w, i) {
                var rank = i + 1;
                var rankClass = rank === 1 ? 'gold' : rank === 2 ? 'silver' : rank === 3 ? 'bronze' : '';
                var color = w.color || '#6366f1';
                var initials = (w.username || 'U').substring(0, 2).toUpperCase();
                html += '<div class="tw-row">';
                html += '<div class="tw-rank ' + rankClass + '">' + (rank <= 3 ? ['🥇', '🥈', '🥉'][rank - 1] : rank) + '</div>';
                html += '<div class="tw-avatar" style="background:' + color + '">' + initials + '</div>';
                html += '<div class="tw-info"><div class="tw-name">' + (w.username || 'Player') + '</div><div class="tw-game">' + (w.game || 'Casino') + '</div></div>';
                html += '<div class="tw-amount"><div class="tw-val">+' + (w.win_amount || 0).toFixed(2) + '</div><div class="tw-mult">x' + (w.multiplier || 0).toFixed(1) + '</div></div>';
                html += '</div>';
            });
            el.innerHTML = html;
        }

        /* === SEARCH === */
        var ALL_GAMES = [
            { id: 'ruby_slots', name: T.slotName || 'Ruby Slots', emoji: '🎰', tag: T.slotTag || 'POPULAR', screen: 'game', bg: '#ff416c', provider: 'rubybet' },
            { id: 'crash', name: T.crashName || 'Crash', emoji: '📈', tag: T.hot || 'HOT', screen: 'crash', bg: '#38ef7d', provider: 'rubybet' },
            { id: 'dice', name: T.diceName || 'Ruby Dice', emoji: '🎲', tag: T.comingTag || 'SOON', screen: null, bg: '#4A00E0', provider: 'rubybet' },
            { id: 'mines', name: T.mineName || 'Mines', emoji: '💣', tag: T.comingTag || 'SOON', screen: null, bg: '#1565C0', provider: 'rubybet' },
            { id: 'plinko', name: 'Plinko', emoji: '⚪', tag: 'SOON', screen: null, bg: '#f59e0b', provider: 'pragmatic' },
            { id: 'roulette', name: 'Roulette', emoji: '🎡', tag: 'SOON', screen: null, bg: '#ef4444', provider: 'evolution' },
            { id: 'blackjack', name: 'Blackjack', emoji: '🃏', tag: 'SOON', screen: null, bg: '#10b981', provider: 'evolution' },
            { id: 'sweet_bonanza', name: 'Sweet Bonanza', emoji: '🍬', tag: 'SOON', screen: null, bg: '#ec4899', provider: 'pragmatic' },
            { id: 'gates_olympus', name: 'Gates of Olympus', emoji: '⚡', tag: 'SOON', screen: null, bg: '#6366f1', provider: 'pragmatic' },
            { id: 'big_bass', name: 'Big Bass Bonanza', emoji: '🐟', tag: 'SOON', screen: null, bg: '#14b8a6', provider: 'pragmatic' },
            { id: 'starlight', name: 'Starlight Princess', emoji: '👸', tag: 'SOON', screen: null, bg: '#8b5cf6', provider: 'pgsoft' },
            { id: 'wanted', name: 'Wanted Dead or Wild', emoji: '🤠', tag: 'SOON', screen: null, bg: '#b92b27', provider: 'hacksaw' }
        ];
        function openSearch() {
            document.getElementById('searchOverlay').classList.add('open');
            setTimeout(function () { document.getElementById('searchInput').focus(); }, 100);
        }
        function closeSearch() {
            document.getElementById('searchOverlay').classList.remove('open');
            document.getElementById('searchInput').value = '';
        }
        function onSearchInput(val) {
            var el = document.getElementById('searchResults');
            if (!val || val.length < 1) {
                el.innerHTML = '<div class="search-empty"><span class="material-symbols-outlined" style="font-size:48px;display:block;margin-bottom:8px">search</span>' + (LANG === 'ru' ? 'Введите название игры' : LANG === 'ua' ? 'Введіть назву гри' : LANG === 'pl' ? 'Wpisz nazwę gry' : 'Type to search games') + '</div>';
                return;
            }
            var q = val.toLowerCase();
            var results = ALL_GAMES.filter(function (g) { return g.name.toLowerCase().indexOf(q) > -1 });
            if (results.length === 0) {
                el.innerHTML = '<div class="search-empty"><span class="material-symbols-outlined" style="font-size:48px;display:block;margin-bottom:8px">search_off</span>' + (LANG === 'ru' ? 'Ничего не найдено' : LANG === 'ua' ? 'Нічого не знайдено' : LANG === 'pl' ? 'Nie znaleziono' : 'No results found') + '</div>';
                return;
            }
            el.innerHTML = results.map(function (g) {
                var isFav = favorites.indexOf(g.id) > -1;
                return '<div class="search-result-item" onclick="' + (g.screen ? 'closeSearch();nav(\'' + g.screen + '\')' : '') + '">'
                    + '<div class="search-result-icon" style="background:' + g.bg + '">' + g.emoji + '</div>'
                    + '<div style="flex:1"><div class="search-result-name">' + g.name + '</div><div class="search-result-tag">' + g.tag + (g.provider ? ' · ' + g.provider : '') + '</div></div>'
                    + '<button class="fav-btn' + (isFav ? ' liked' : '') + '" onclick="event.stopPropagation();toggleFavorite(\'' + g.id + '\',this)" style="position:static"><span class="material-symbols-outlined">favorite</span></button>'
                    + '</div>';
            }).join('');
        }

        /* === NOTIFICATION BADGE === */
        function updateBonusBadge() {
            var badge = document.getElementById('bonusBadge');
            if (!badge) return;
            var count = userBonuses && userBonuses.active ? userBonuses.active.length : 0;
            if (count > 0) { badge.textContent = count; badge.style.display = 'flex'; }
            else { badge.style.display = 'none'; }
        }

        function buildGameGrid() {
            var games = ALL_GAMES.slice(0, 4); /* First 4 main games */
            var html = '';
            for (var i = 0; i < 4; i++) {
                html += ALL_GAMES.map(function (g) {
                    var isSoon = g.tag === 'SOON' || g.tag === 'СКОРО' || g.tag === 'НЕЗАБАРОМ' || g.tag === 'WKRÓTCE';
                    var isFav = favorites.indexOf(g.id) > -1;
                    var badgeHtml = g.tag ? '<div class="absolute top-2 left-2 text-[9px] font-[800] uppercase px-[8px] py-[2px] rounded-[4px] tracking-[0.5px] z-10 ' + (isSoon ? 'bg-surface2 text-dim' : 'bg-red text-white') + '">' + g.tag + '</div>' : '';
                    var favHtml = '<button class="fav-btn' + (isFav ? ' liked' : '') + '" onclick="event.stopPropagation();toggleFavorite(\'' + g.id + '\',this)"><span class="material-symbols-outlined">favorite</span></button>';
                    return '<div class="relative rounded-lg overflow-hidden bg-surface border border-border cursor-pointer transition-transform active:scale-95" data-game-id="' + g.id + '" data-provider="' + (g.provider || '') + '" onclick="' + (g.screen ? 'nav(\'' + g.screen + '\')' : '') + '">'
                        + badgeHtml + favHtml
                        + '<div class="w-full aspect-[4/3] flex items-center justify-center text-[42px] relative">'
                        + '<div class="absolute inset-0 opacity-40" style="background:' + (g.bg || '#333') + '"></div>'
                        + '<div class="relative z-10">' + g.emoji + '</div>'
                        + '</div>'
                        + '<div class="p-[10px]">'
                        + '<div class="font-[Montserrat] text-[12px] font-[800] uppercase tracking-[0.3px] whitespace-nowrap overflow-hidden text-ellipsis">' + g.name + '</div>'
                        + '<div class="text-[10px] text-dim font-[500] mt-[2px]">' + (g.provider ? g.provider.charAt(0).toUpperCase() + g.provider.slice(1) : '') + ' · ' + g.tag + '</div>'
                        + '</div></div>';
                }).join('');
            }
            document.getElementById('gameGrid').innerHTML = html;
        }

        function initBonuses() {
            loadBonuses();
            buildBonusPills();
        }

        function buildBonusPills() {
            var pillLabels = ['All', 'Deposit', 'Free Spins', 'VIP', 'Cashback'];
            if (LANG === 'ru') pillLabels = ['Все', 'Депозит', 'Фриспины', 'VIP', 'Кэшбек'];
            if (LANG === 'ua') pillLabels = ['Все', 'Депозит', 'Фріспіни', 'VIP', 'Кешбек'];
            if (LANG === 'pl') pillLabels = ['Wszystkie', 'Depozyt', 'Darmowe Spiny', 'VIP', 'Cashback'];
            var bp = document.getElementById('bonusPills');
            if (bp) {
                bp.className = 'flex gap-[8px] px-[16px] mb-[16px] overflow-x-auto no-scrollbar';
                bp.innerHTML = pillLabels.map(function (p, i) {
                    return '<div class="pill' + (i === 0 ? ' active' : '') + '" onclick="this.parentNode.querySelectorAll(\'.pill\').forEach(function(e){e.classList.remove(\'active\')});this.classList.add(\'active\')">' + p + '</div>';
                }).join('');
            }
        }

        /* === PERSONAL BONUS SYSTEM === */
        function switchBonusTab(tab) {
            document.getElementById('segActive').classList.toggle('active', tab === 'active');
            document.getElementById('segHistory').classList.toggle('active', tab === 'history');
            document.getElementById('bonusActivePanel').style.display = tab === 'active' ? 'block' : 'none';
            document.getElementById('bonusHistoryPanel').style.display = tab === 'history' ? 'block' : 'none';
        }

        /* Fallback demo data — used when API is unavailable */
        var userBonuses = {
            balance: 150.00,
            active: [
                { id: 1, bonus_type: 'cashback', title: 'Weekly Cashback', description: 'Earn 10% back on all weekly losses', icon: 'payments', progress: 85.5, max_progress: 100, amount: 85.50, vip_tag: '', expires_at: '', status: 'active', badge: 'CASHBACK' },
                { id: 2, bonus_type: 'free_spins', title: 'Loyalty Free Spins', description: "50 Spins on 'Ruby Reels' Deluxe", icon: 'casino', progress: 0, max_progress: 0, amount: 50, vip_tag: 'VIP GOLD', expires_at: '2026-02-24 15:00:00', status: 'active', badge: 'FREE SPINS' },
                { id: 3, bonus_type: 'deposit_match', title: 'Deposit Match', description: 'Wager $200 more to unlock $50 cash', icon: 'trophy', progress: 120, max_progress: 200, amount: 50, vip_tag: '', expires_at: '', status: 'active', badge: 'DEPOSIT MATCH' }
            ],
            history: [
                { id: 10, title: 'Welcome Free Bet', claimed_at: '2023-09-28', amount: 50.00, status: 'completed', badge: 'DEPOSIT MATCH', icon: 'redeem' },
                { id: 11, title: 'Weekly Reload Boost', claimed_at: '2023-10-05', amount: 25.00, status: 'expired', badge: 'RELOAD', icon: 'timer_off' },
                { id: 12, title: 'UCL Finals Cashback', claimed_at: '2023-09-15', amount: 120.50, status: 'completed', badge: 'CASHBACK', icon: 'sports_soccer' },
                { id: 13, title: 'Referral Reward', claimed_at: '2023-08-22', amount: 10.00, status: 'expired', badge: 'REFERRAL', icon: 'confirmation_number' }
            ]
        };

        async function loadBonuses() {
            try {
                var r = await fetch(API + '/api/bonuses?' + qs()); var d = await r.json();
                if (d.ok) {
                    userBonuses.balance = d.balance || 0;
                    if (d.active && d.active.length > 0) userBonuses.active = d.active;
                    if (d.history && d.history.length > 0) userBonuses.history = d.history;
                }
            } catch (e) { }
            renderActiveBonuses(); renderBonusHistory(); updateBonusBadge();
        }

        function renderActiveBonuses() {
            var b = userBonuses;
            var elBal = document.getElementById('bonusBalAmount');
            if (elBal) elBal.textContent = '$' + b.balance.toFixed(2);
            var elCount = document.getElementById('activeBonusCount');
            if (elCount) elCount.textContent = b.active.length + ' Active';
            var html = '';
            b.active.forEach(function (a) {
                /* Card with left red border accent */
                html += '<div class="glass-card" style="border-left:3px solid var(--red)">';
                html += '<div class="gc-bg-icon"><span class="material-symbols-outlined">' + (a.icon || 'redeem') + '</span></div>';
                /* Title + VIP tag */
                html += '<div style="display:flex;justify-content:space-between;align-items:flex-start;position:relative;z-index:1;margin-bottom:2px">';
                html += '<div class="gc-title">' + a.title + '</div>';
                if (a.vip_tag) html += '<span class="gc-vip-tag">' + a.vip_tag + '</span>';
                html += '</div>';
                html += '<div class="gc-desc">' + (a.description || '') + '</div>';

                /* Timer (if expires_at is set and in the future) */
                if (a.expires_at) {
                    var remaining = getTimeRemaining(a.expires_at);
                    if (remaining) html += '<div class="gc-timer"><span class="material-symbols-outlined">timer</span><div><div class="gc-timer-label">Expires In</div><div class="gc-timer-val">' + remaining + '</div></div></div>';
                }

                /* Progress bar */
                if (a.max_progress > 0) {
                    var pct = Math.min(100, Math.round(a.progress / a.max_progress * 100));
                    var label = a.bonus_type === 'deposit_match' ? 'Wagering Requirement' : 'Progress';
                    html += '<div class="gc-progress"><div class="gc-progress-header"><span class="label">' + label + '</span><span class="val">';
                    if (a.bonus_type === 'deposit_match') html += pct + '%';
                    else html += '$' + a.progress.toFixed(2) + ' / $' + a.max_progress.toFixed(2) + ' Max';
                    html += '</span></div><div class="gc-progress-bar"><div class="gc-progress-fill" style="width:' + pct + '%"></div></div></div>';
                }

                /* Note for deposit match */
                if (a.bonus_type === 'deposit_match') html += '<div style="font-size:10px;color:var(--dim2);font-style:italic;margin-bottom:14px;position:relative;z-index:1">Eligible on Sports and Casino slots.</div>';

                /* Button */
                if (a.bonus_type === 'cashback' && a.progress > 0) {
                    html += '<button class="gc-btn-primary" onclick="claimBonus(' + a.id + ',' + a.progress + ')">Claim $' + a.progress.toFixed(2) + '</button>';
                } else if (a.bonus_type === 'free_spins') {
                    html += '<button class="gc-btn-primary" onclick="activateBonus(' + a.id + ')">Activate Now</button>';
                } else {
                    html += '<button class="gc-btn-outline" onclick="viewBonusDetails(' + a.id + ')">View Details</button>';
                }
                html += '</div>';
            });
            if (b.active.length === 0) {
                html += '<div style="text-align:center;padding:40px 0;opacity:.4"><span class="material-symbols-outlined" style="font-size:40px;display:block;margin-bottom:6px">redeem</span><span style="font-size:12px">No active bonuses</span></div>';
            }
            document.getElementById('activeBonusList').innerHTML = html;
        }

        function renderBonusHistory() {
            var h = userBonuses.history;
            var html = '';
            h.forEach(function (item) {
                var isExpired = item.status === 'expired';
                var dateStr = item.claimed_at || item.created_at || '';
                var dateLabel = isExpired ? 'Expired ' : 'Claimed ';
                if (dateStr.length >= 10) dateLabel += formatBonusDate(dateStr);

                html += '<div class="history-item' + (isExpired ? ' expired' : '') + '" style="border-left:3px solid ' + (isExpired ? 'var(--border)' : 'var(--red)') + '">';

                /* Top: icon + info + amount */
                html += '<div class="hi-top"><div style="display:flex;align-items:flex-start;gap:10px"><div class="hi-icon ' + (isExpired ? 'inactive' : 'active') + '"><span class="material-symbols-outlined" style="color:' + (isExpired ? 'var(--dim2)' : 'var(--red)') + ';font-variation-settings:\'FILL\' ' + (isExpired ? '0' : '1') + '">' + (item.icon || 'redeem') + '</span></div>';
                html += '<div class="hi-info"><div class="hi-title">' + item.title + '</div><div class="hi-date">' + dateLabel + '</div></div></div>';
                html += '<div class="hi-amount"><div class="hi-val"' + (isExpired ? ' style="color:var(--dim2)"' : '') + '>$' + (item.amount || 0).toFixed(2) + '</div><div class="hi-val-label">Value</div></div></div>';

                /* Bottom: status + badge */
                html += '<div class="hi-bottom"><div class="hi-status ' + (isExpired ? '' : 'completed') + '">';
                if (isExpired) html += '<span class="material-symbols-outlined">cancel</span><span>Expired</span>';
                else html += '<span class="material-symbols-outlined" style="font-variation-settings:\'FILL\' 1">check_circle</span><span>Completed</span>';
                html += '</div><span class="hi-badge">' + (item.badge || item.bonus_type || 'BONUS') + '</span></div>';
                html += '</div>';
            });
            if (h.length === 0) {
                html += '<div style="text-align:center;padding:30px 0;opacity:.4"><span style="font-size:12px">No bonus history yet</span></div>';
            }
            // Temporarily mapping bonusHistoryList to nothing since it was moved to Profile screen but removed from it to save space
            var hl = document.getElementById('bonusHistoryList');
            if (hl) hl.innerHTML = html;
        }

        function getTimeRemaining(dateStr) {
            try {
                var end = new Date(dateStr.replace(' ', 'T')); var now = new Date();
                var diff = end - now; if (diff <= 0) return null;
                var h = Math.floor(diff / 3600000); var m = Math.floor((diff % 3600000) / 60000); var s = Math.floor((diff % 60000) / 1000);
                return (h < 10 ? '0' : '') + h + 'h : ' + (m < 10 ? '0' : '') + m + 'm : ' + (s < 10 ? '0' : '') + s + 's';
            } catch (e) { return null }
        }

        function formatBonusDate(d) {
            try {
                var dt = new Date(d.replace(' ', 'T'));
                var months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                return months[dt.getMonth()] + ' ' + dt.getDate() + ', ' + dt.getFullYear();
            } catch (e) { return d }
        }

        async function claimBonus(id, amount) {
            try {
                var r = await fetch(API + '/api/claim-bonus', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(Object.assign({}, auth(), { bonus_id: id })) });
                var d = await r.json();
                if (d.ok) {
                    showToast('✅', 'Claimed $' + (amount || 0).toFixed(2) + '!', 'OK', '', function () { closeToast() });
                    loadBalance(); loadBonuses();
                } else {
                    showToast('❌', d.error || 'Failed to claim', 'OK', '', function () { closeToast() });
                }
            } catch (e) { showToast('❌', 'Network error', 'OK', '', function () { closeToast() }) }
        }

        async function activateBonus(id) {
            try {
                var r = await fetch(API + '/api/activate-bonus', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(Object.assign({}, auth(), { bonus_id: id })) });
                var d = await r.json();
                if (d.ok) {
                    var msg = d.free_spins_added ? '+' + d.free_spins_added + ' Free Spins!' : 'Bonus activated!';
                    showToast('⚡', msg, 'OK', '', function () { closeToast() });
                    loadBalance(); loadBonuses();
                } else {
                    showToast('❌', d.error || 'Failed', 'OK', '', function () { closeToast() });
                }
            } catch (e) { showToast('❌', 'Network error', 'OK', '', function () { closeToast() }) }
        }

        function viewBonusDetails(id) {
            var bonus = userBonuses.active.find(function (b) { return b.id === id });
            if (bonus && bonus.max_progress > 0) {
                var remaining = (bonus.max_progress - bonus.progress).toFixed(2);
                showToast('ℹ️', 'Wager $' + remaining + ' more to unlock $' + bonus.amount.toFixed(2), 'OK', '', function () { closeToast() });
            } else {
                showToast('ℹ️', 'View details', 'OK', '', function () { closeToast() });
            }
        }

        function initBonuses() { loadBonuses() }

        function buildWalletPackages() {
            var pkgs = [{ amount: '50', price: '0.50' }, { amount: '100', price: '0.90' }, { amount: '500', price: '4.00' }];
            document.getElementById('assetRow').innerHTML = pkgs.map(function (p, i) {
                return '<button class="asset-btn' + (i === 0 ? ' active' : '') + '" onclick="selectPkg(this,\'' + p.amount + '\',\'' + p.price + '\')" data-coins="' + p.amount + '" data-price="' + p.price + '">' + p.amount + ' coins<br><span style="font-size:10px;color:var(--dim)">$' + p.price + '</span></button>';
            }).join('');
            /* Stars packages */
            var starPkgs = [{ stars: 50, price: '50' }, { stars: 150, price: '150' }, { stars: 500, price: '500' }];
            var sr = document.getElementById('starsRow');
            if (sr) sr.innerHTML = starPkgs.map(function (p, i) {
                return '<button class="asset-btn' + (i === 0 ? ' active' : '') + '" onclick="selectPkg(this,\'' + p.stars + '\',\'' + p.price + '\')" data-stars="' + p.stars + '" data-price="' + p.price + '">⭐ ' + p.stars + '<br><span style="font-size:10px;color:var(--dim)">' + p.price + ' ⭐</span></button>';
            }).join('');
        }

        function selectPkg(el, amount, price) {
            document.querySelectorAll('.asset-btn').forEach(function (b) { b.classList.remove('active') });
            el.classList.add('active');
        }
        var selectedPkg = { coins: '50', price: '0.50' };
        function selectPkg(el, amount, price) {
            el.parentNode.querySelectorAll('.asset-btn').forEach(function (b) { b.classList.remove('active') });
            el.classList.add('active');
            selectedPkg = { coins: amount, price: price };
        }

        /* === CURRENCY SYSTEM === */
        var RATES = { USDT: 1, USD: 1, PLN: 4.05, UAH: 41.2, EUR: 0.92, RUB: 96.5 };
        var displayCurrency = 'USDT';
        var usdtBalance = 0; /* internal USDT balance (cents precision) */
        var starsBalance = 0;
        var payMethod = 'crypto'; /* crypto | card | stars */

        function setCurrency(cur) {
            displayCurrency = cur;
            document.querySelectorAll('#currencyRow .pill').forEach(function (p) { p.classList.toggle('active', p.getAttribute('data-cur') === cur) });
            updateWallet();
            updateBalanceUI();
        }

        function formatCurrency(usdtAmount, cur) {
            if (!cur) cur = displayCurrency;
            var val = usdtAmount * RATES[cur];
            var symbols = { USDT: '', USD: '$', PLN: 'zł', UAH: '₴', EUR: '€', RUB: '₽' };
            if (cur === 'USDT') return val.toFixed(2);
            return symbols[cur] + val.toFixed(2);
        }

        function updateWallet() {
            var el = document.getElementById('wBalAmount');
            if (el) {
                if (displayCurrency === 'USDT') {
                    el.textContent = usdtBalance.toFixed(2);
                    document.getElementById('wBalUnit').textContent = 'USDT';
                } else {
                    el.textContent = formatCurrency(usdtBalance);
                    document.getElementById('wBalUnit').textContent = displayCurrency;
                }
            }
            var loc = document.getElementById('wBalLocal');
            if (loc) {
                if (displayCurrency !== 'USDT') loc.textContent = '≈ ' + usdtBalance.toFixed(2) + ' USDT';
                else loc.textContent = '';
            }
            var se = document.getElementById('wStarsAmount');
            if (se) se.textContent = starsBalance;
        }

        function updateBalanceUI() {
            var hb = document.getElementById('headerBal');
            var hu = document.getElementById('headerUnit');
            if (activeWallet === 'stars') {
                /* Stars mode — show stars balance */
                if (hb) hb.textContent = starsBalance;
                if (hu) hu.textContent = '⭐';
            } else {
                /* USDT mode — show in selected display currency */
                if (hb) {
                    if (usdtBalance !== null && usdtBalance !== undefined) {
                        hb.textContent = displayCurrency === 'USDT' ? usdtBalance.toFixed(2) : formatCurrency(usdtBalance);
                    } else {
                        hb.textContent = '...';
                    }
                }
                if (hu) hu.textContent = displayCurrency;
            }
            /* Game balance — always show active wallet */
            var gb = document.getElementById('gameBal');
            var cb = document.getElementById('crashBal');
            if (gb) {
                if (activeWallet === 'stars') {
                    gb.textContent = starsBalance + ' ⭐';
                } else {
                    gb.textContent = usdtBalance !== null ? usdtBalance.toFixed(2) : '0';
                }
            }
            if (cb) {
                if (activeWallet === 'stars') {
                    cb.textContent = starsBalance + ' ⭐';
                } else {
                    cb.textContent = usdtBalance !== null ? usdtBalance.toFixed(2) : '0';
                }
            }
            /* Header dual balance */
            var hb = document.getElementById('headerBal');
            var hsv = document.getElementById('headerBalStarsVal');
            if (hb) {
                if (usdtBalance !== null && usdtBalance !== undefined) {
                    hb.textContent = displayCurrency === 'USDT' ? usdtBalance.toFixed(2) : formatCurrency(usdtBalance);
                } else {
                    hb.textContent = '...';
                }
            }
            if (hsv) hsv.textContent = starsBalance;
            /* Popup values */
            var pu = document.getElementById('bpUsdtVal');
            var ps = document.getElementById('bpStarsVal');
            if (pu) pu.textContent = '$' + (usdtBalance || 0).toFixed(2);
            if (ps) ps.textContent = starsBalance || 0;
            var fb = document.getElementById('freeBadge'); if (fb) fb.textContent = freeSpins > 0 ? '⚡ ' + freeSpins + ' ' + T.freeSpins : '';
            updateSpinBtn();
        }

        /* Override loadBalance to set usdtBalance */
        async function loadBalance() {
            try {
                var r = await fetch(API + '/api/balance?' + qs()); var d = await r.json();
                if (d.ok) {
                    balance = d.balance; freeSpins = d.free_spins || 0;
                    /* Convert coins to USDT — 100 coins = $1 USDT */
                    usdtBalance = d.balance / 100;
                    starsBalance = d.stars_balance || 0;
                    updateBalanceUI(); updateWallet();
                    if (d.vip) updateVIP(d.vip);
                    return;
                }
            } catch (e) { }
            setTimeout(loadBalance, 2000);
        }

        /* === WALLET TAB SWITCH (legacy — now using cashier tabs) === */
        function switchWalletTab(tab) {
            /* Legacy compatibility */
        }

        /* === CASHIER TAB SYSTEM === */
        function switchCashierTab(tab) {
            ['deposit', 'withdraw', 'history'].forEach(function (t) {
                var el = document.getElementById('cash' + t.charAt(0).toUpperCase() + t.slice(1));
                var tb = document.getElementById('cashTab' + t.charAt(0).toUpperCase() + t.slice(1));
                if (el) el.style.display = t === tab ? 'block' : 'none';
                if (tb) tb.classList.toggle('active', t === tab);
            });
            if (tab === 'history') loadTransactionHistory();
            if (tab === 'withdraw') updateWithdrawInfo();
        }

        function switchActiveWallet(w) {
            activeWallet = w;
            updateBalanceUI(); updateWallet();
            /* Highlight active card in cashier */
            var uc = document.getElementById('cashierUsdtCard');
            var sc = document.getElementById('cashierStarsCard');
            if (uc) uc.style.borderColor = w === 'usdt' ? 'var(--red)' : 'var(--border)';
            if (sc) sc.style.borderColor = w === 'stars' ? '#FFD700' : 'var(--border)';
            /* Header highlight */
            var hc = document.getElementById('headerBalCrypto');
            var hs = document.getElementById('headerBalStars');
            if (hc) hc.style.background = w === 'usdt' ? 'rgba(227,30,36,.1)' : 'transparent';
            if (hs) hs.style.background = w === 'stars' ? 'rgba(255,215,0,.1)' : 'transparent';
            if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.HapticFeedback) window.Telegram.WebApp.HapticFeedback.impactOccurred('light');
        }

        /* === PAYMENT METHOD === */
        function selectPayMethod(method) {
            payMethod = method;
            /* Crypto */
            document.getElementById('pmCrypto').style.borderColor = method === 'crypto' ? 'var(--red)' : 'var(--border)';
            document.querySelector('#pmCrypto .material-symbols-outlined:last-child').textContent = method === 'crypto' ? 'check_circle' : 'radio_button_unchecked';
            document.querySelector('#pmCrypto .material-symbols-outlined:last-child').style.color = method === 'crypto' ? 'var(--red)' : 'var(--dim)';
            /* Stars */
            var pmStars = document.getElementById('pmStars');
            if (pmStars) {
                pmStars.style.borderColor = method === 'stars' ? '#FFD700' : 'var(--border)';
                document.getElementById('pmStarsCheck').textContent = method === 'stars' ? 'check_circle' : 'radio_button_unchecked';
                document.getElementById('pmStarsCheck').style.color = method === 'stars' ? '#FFD700' : 'var(--dim)';
            }
            /* Card */
            document.getElementById('pmCard').style.borderColor = method === 'card' ? 'var(--red)' : 'var(--border)';
            document.getElementById('pmCardCheck').textContent = method === 'card' ? 'check_circle' : 'radio_button_unchecked';
            document.getElementById('pmCardCheck').style.color = method === 'card' ? 'var(--red)' : 'var(--dim)';
            /* Show/hide sections */
            var cs = document.getElementById('depositCryptoSection');
            var ss = document.getElementById('depositStarsSection');
            if (cs) cs.style.display = (method === 'crypto' || method === 'card') ? 'block' : 'none';
            if (ss) ss.style.display = method === 'stars' ? 'block' : 'none';
        }

        /* === WITHDRAW === */
        var withdrawMethod = 'crypto';
        function selectWithdrawMethod(m) {
            withdrawMethod = m;
            document.getElementById('wdCrypto').classList.toggle('active', m === 'crypto');
            document.getElementById('wdStars').classList.toggle('active', m === 'stars');
            document.getElementById('wdUnit').textContent = m === 'crypto' ? displayCurrency : 'Stars';
            updateWithdrawInfo();
        }
        function setWithdrawPct(pct) {
            var bal = withdrawMethod === 'crypto' ? usdtBalance : starsBalance;
            var amt = (bal * pct / 100);
            document.getElementById('withdrawAmount').value = withdrawMethod === 'crypto' ? amt.toFixed(2) : Math.floor(amt);
        }
        function updateWithdrawInfo() {
            var bal = withdrawMethod === 'crypto' ? usdtBalance : starsBalance;
            var unit = withdrawMethod === 'crypto' ? displayCurrency : 'Stars';
            document.getElementById('wdAvailable').textContent = (withdrawMethod === 'crypto' ? bal.toFixed(2) : bal) + ' ' + unit;
        }
        async function submitWithdraw() {
            var amt = parseFloat(document.getElementById('withdrawAmount').value);
            if (!amt || amt <= 0) { showToast('❌', 'Enter valid amount', 'OK', '', function () { closeToast() }); return; }
            if (withdrawMethod === 'crypto' && amt < 5) { showToast('❌', 'Minimum withdrawal: $5.00', 'OK', '', function () { closeToast() }); return; }
            if (withdrawMethod === 'crypto' && amt > usdtBalance) { showToast('❌', 'Insufficient balance', 'OK', '', function () { closeToast() }); return; }
            if (withdrawMethod === 'stars' && amt > starsBalance) { showToast('❌', 'Insufficient Stars', 'OK', '', function () { closeToast() }); return; }
            try {
                showToast('⏳', 'Processing withdrawal...', '⏳', '', null);
                var r = await fetch(API + '/api/withdraw', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(Object.assign({}, auth(), { amount: amt, method: withdrawMethod })) });
                var d = await r.json(); closeToast();
                if (d.ok) {
                    showToast('✅', 'Withdrawal request submitted! ' + (withdrawMethod === 'crypto' ? '$' + amt.toFixed(2) : amt + ' ⭐'), 'OK', '', function () { closeToast() });
                    loadBalance();
                } else {
                    showToast('❌', d.error || 'Withdrawal failed', 'OK', '', function () { closeToast() });
                }
            } catch (e) { closeToast(); showToast('❌', 'Network error', 'OK', '', function () { closeToast() }); }
        }

        /* === TRANSACTION HISTORY === */
        async function loadTransactionHistory() {
            var el = document.getElementById('txHistoryList');
            if (!el) return;
            el.innerHTML = '<div style="text-align:center;padding:30px 0;opacity:.5"><span class="material-symbols-outlined" style="font-size:24px;animation:spin 1s linear infinite">sync</span></div>';
            try {
                var r = await fetch(API + '/api/transactions?' + qs());
                var d = await r.json();
                if (d.ok && d.transactions && d.transactions.length > 0) {
                    renderTransactions(d.transactions);
                    return;
                }
            } catch (e) { }
            /* Demo fallback */
            el.innerHTML = '<div style="text-align:center;padding:40px 0;opacity:.4"><span class="material-symbols-outlined" style="font-size:40px;display:block;margin-bottom:6px">receipt_long</span><span style="font-size:12px">No transactions yet</span></div>';
        }
        function renderTransactions(txs) {
            var el = document.getElementById('txHistoryList');
            var html = '';
            txs.forEach(function (tx) {
                var isDeposit = tx.type === 'deposit';
                var icon = isDeposit ? 'arrow_downward' : 'arrow_upward';
                var color = isDeposit ? 'var(--green)' : 'var(--red)';
                var sign = isDeposit ? '+' : '-';
                var statusColor = tx.status === 'completed' ? 'var(--green)' : tx.status === 'pending' ? '#FFD700' : 'var(--dim)';
                html += '<div style="display:flex;align-items:center;gap:10px;padding:12px;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);margin-bottom:6px">';
                html += '<div style="width:36px;height:36px;border-radius:50%;background:' + (isDeposit ? 'rgba(34,197,94,.08)' : 'rgba(227,30,36,.08)') + ';display:flex;align-items:center;justify-content:center"><span class="material-symbols-outlined" style="font-size:18px;color:' + color + '">' + icon + '</span></div>';
                html += '<div style="flex:1"><div style="font-size:12px;font-weight:700;color:#fff;text-transform:capitalize">' + tx.type + '</div><div style="font-size:10px;color:var(--dim)">' + (tx.method || '') + ' · ' + (tx.date || '') + '</div></div>';
                html += '<div style="text-align:right"><div style="font-size:13px;font-weight:800;color:' + color + ';font-family:\'Montserrat\',sans-serif">' + sign + (tx.amount || 0) + '</div><div style="font-size:9px;font-weight:700;color:' + statusColor + ';text-transform:uppercase">' + (tx.status || '') + '</div></div>';
                html += '</div>';
            });
            el.innerHTML = html;
        }

        /* === DEPOSIT FLOW (inside miniapp) === */
        function openDepositModal(type) {
            if (type === 'stars') {
                /* Telegram Stars payment via WebApp invoice */
                var starsPkg = document.querySelector('#starsRow .asset-btn.active');
                var amount = starsPkg ? starsPkg.getAttribute('data-stars') : '50';
                buyStars(parseInt(amount));
                return;
            }
            if (payMethod === 'crypto') {
                /* CryptoBot payment — call backend to create invoice, open URL in browser */
                var pkg = document.querySelector('#assetRow .asset-btn.active');
                var coins = pkg ? pkg.getAttribute('data-coins') : '50';
                var price = pkg ? pkg.getAttribute('data-price') : '0.50';
                buyCrypto(coins, price);
            } else if (payMethod === 'card') {
                /* Card payment — call backend to get payment link */
                var pkg2 = document.querySelector('#assetRow .asset-btn.active');
                var coins2 = pkg2 ? pkg2.getAttribute('data-coins') : '50';
                var price2 = pkg2 ? pkg2.getAttribute('data-price') : '0.50';
                buyCard(coins2, price2);
            }
        }

        async function buyStars(amount) {
            /* Request invoice link from backend, then open via Telegram WebApp */
            try {
                showToast('⭐', LANG === 'ru' ? 'Создаём счёт...' : LANG === 'ua' ? 'Створюємо рахунок...' : LANG === 'pl' ? 'Tworzenie faktury...' : 'Creating invoice...', '⏳', '', null);
                var r = await fetch(API + '/api/create-stars-invoice', {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(Object.assign({}, auth(), { stars: amount }))
                });
                var d = await r.json();
                closeToast();
                if (d.ok && d.invoice_link) {
                    tg.openInvoice(d.invoice_link, function (status) {
                        if (status === 'paid') {
                            showToast('✅', LANG === 'ru' ? 'Оплата прошла! +' + amount + ' ⭐' : LANG === 'ua' ? 'Оплата пройшла! +' + amount + ' ⭐' : LANG === 'pl' ? 'Płatność przeszła! +' + amount + ' ⭐' : 'Payment successful! +' + amount + ' ⭐', 'OK', '', function () { closeToast() });
                            loadBalance();
                        } else if (status === 'cancelled') {
                            /* User cancelled, do nothing */
                        } else if (status === 'failed') {
                            showToast('❌', LANG === 'ru' ? 'Ошибка оплаты' : LANG === 'ua' ? 'Помилка оплати' : LANG === 'pl' ? 'Błąd płatności' : 'Payment failed', 'OK', '', function () { closeToast() });
                        }
                    });
                } else {
                    showToast('❌', d.error || 'Error creating invoice', 'OK', '', function () { closeToast() });
                }
            } catch (e) {
                closeToast();
                showToast('❌', 'Network error', 'OK', '', function () { closeToast() });
            }
        }

        async function buyCrypto(coins, price) {
            try {
                showToast('💎', LANG === 'ru' ? 'Создаём счёт CryptoBot...' : LANG === 'ua' ? 'Створюємо рахунок CryptoBot...' : LANG === 'pl' ? 'Tworzenie faktury CryptoBot...' : 'Creating CryptoBot invoice...', '⏳', '', null);
                var r = await fetch(API + '/api/create-invoice', {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(Object.assign({}, auth(), { coins: parseInt(coins), amount: parseFloat(price) }))
                });
                var d = await r.json();
                closeToast();
                if (d.ok && d.pay_url) {
                    /* CryptoBot mini_app_invoice_url is a t.me link — open inside Telegram */
                    var url = d.pay_url;
                    if (url.indexOf('t.me/') !== -1) {
                        tg.openTelegramLink(url);
                    } else {
                        /* fallback: open inside Telegram's webview */
                        tg.openLink(url, { try_instant_view: true });
                    }
                    pollPayment(d.invoice_id || null);
                } else {
                    showToast('❌', d.error || 'Error creating invoice', 'OK', '', function () { closeToast() });
                }
            } catch (e) {
                closeToast();
                showToast('❌', 'Network error', 'OK', '', function () { closeToast() });
            }
        }

        async function buyCard(coins, price) {
            try {
                showToast('💳', LANG === 'ru' ? 'Создаём платёж...' : LANG === 'ua' ? 'Створюємо платіж...' : LANG === 'pl' ? 'Tworzenie płatności...' : 'Creating payment...', '⏳', '', null);
                var r = await fetch(API + '/api/create-card-payment', {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(Object.assign({}, auth(), { coins: parseInt(coins), amount: parseFloat(price) }))
                });
                var d = await r.json();
                closeToast();
                if (d.ok && d.pay_url) {
                    /* Open card payment inside Telegram webview */
                    tg.openLink(d.pay_url, { try_instant_view: true });
                    pollPayment(d.invoice_id || null);
                } else {
                    var msg = d.error || (LANG === 'ru' ? 'Оплата картой скоро будет доступна' : LANG === 'ua' ? 'Оплата карткою скоро буде доступна' : LANG === 'pl' ? 'Płatność kartą wkrótce dostępna' : 'Card payment coming soon');
                    showToast('💳', msg, 'OK', '', function () { closeToast() });
                }
            } catch (e) {
                closeToast();
                showToast('❌', 'Network error', 'OK', '', function () { closeToast() });
            }
        }

        /* Poll backend for payment completion */
        var pollTimer = null;
        function pollPayment(invoiceId) {
            var attempts = 0;
            if (pollTimer) clearInterval(pollTimer);
            pollTimer = setInterval(async function () {
                attempts++;
                if (attempts > 60) { clearInterval(pollTimer); return } /* stop after 5 min */
                try {
                    await loadBalance(); /* reload balance — if payment went through, balance will update */
                } catch (e) { }
            }, 5000);
            /* Auto-stop polling after 5 min */
            setTimeout(function () { if (pollTimer) clearInterval(pollTimer) }, 300000);
        }

        /* === BALANCE POPUP (header tap) === */
        function openBalancePopup() {
            var p = document.getElementById('balPopup');
            p.style.display = 'block';
            /* Update active state */
            document.getElementById('bpUsdt').classList.toggle('active', activeWallet === 'usdt');
            document.getElementById('bpStars').classList.toggle('active', activeWallet === 'stars');
            updateBalPopupContent();
            /* Update currency pills */
            document.querySelectorAll('#bpCurrencies .pill').forEach(function (b) {
                b.classList.toggle('active', b.getAttribute('data-cur') === displayCurrency);
            });
            document.getElementById('bpCurrencies').style.display = activeWallet === 'usdt' ? 'grid' : 'none';
            /* Animate in */
            requestAnimationFrame(function () {
                var card = document.getElementById('balPopupCard');
                card.style.transform = 'translateY(0) scale(1)'; card.style.opacity = '1';
            });
        }
        function closeBalancePopup() {
            var card = document.getElementById('balPopupCard');
            card.style.transform = 'translateY(-8px) scale(.95)'; card.style.opacity = '0';
            setTimeout(function () { document.getElementById('balPopup').style.display = 'none' }, 200);
        }
        function switchBalPopup(type) {
            activeWallet = type;
            document.getElementById('bpUsdt').classList.toggle('active', type === 'usdt');
            document.getElementById('bpStars').classList.toggle('active', type === 'stars');
            document.getElementById('bpCurrencies').style.display = type === 'usdt' ? 'grid' : 'none';
            document.getElementById('bpDeposit').textContent = type === 'stars' ? 'BUY STARS' : 'DEPOSIT';
            updateBalPopupContent();
            updateBalanceUI();
        }
        function updateBalPopupContent() {
            if (activeWallet === 'stars') {
                document.getElementById('bpLabel').textContent = '⭐ STARS BALANCE';
                document.getElementById('bpAmount').textContent = starsBalance + ' ⭐';
                document.getElementById('bpSub').textContent = '';
            } else {
                document.getElementById('bpLabel').textContent = displayCurrency + ' BALANCE';
                var sym = RATES[displayCurrency] ? { USDT: '', USD: '$', PLN: 'zł', UAH: '₴', EUR: '€', RUB: '₽', GBP: '£' }[displayCurrency] || '' : '$';
                document.getElementById('bpAmount').textContent = formatCurrency(usdtBalance);
                document.getElementById('bpSub').textContent = displayCurrency !== 'USDT' ? '≈ ' + usdtBalance.toFixed(2) + ' USDT' : '';
            }
        }
        function setCurrencyPopup(cur) {
            setCurrency(cur);
            document.querySelectorAll('#bpCurrencies .pill').forEach(function (b) {
                b.classList.toggle('active', b.getAttribute('data-cur') === cur);
            });
            updateBalPopupContent();
        }

        /* === LANGUAGE SELECTOR (in-app) === */
        var LANG_OPTIONS = {
            pl: { flag: '🇵🇱', name: 'Polski' },
            ua: { flag: '🇺🇦', name: 'Українська' },
            ru: { flag: '🇷🇺', name: 'Русский' },
            en: { flag: '🇬🇧', name: 'English' }
        };

        function openLangSelector() {
            var ol = document.getElementById('langOverlay');
            ol.style.display = 'flex';
            var list = document.getElementById('langList');
            list.innerHTML = Object.keys(LANG_OPTIONS).map(function (code) {
                var l = LANG_OPTIONS[code];
                var isActive = code === LANG;
                return '<button onclick="setLanguage(\'' + code + '\')" style="display:flex;align-items:center;gap:12px;padding:14px 16px;border-radius:var(--radius);border:' + (isActive ? '1.5px solid var(--red)' : '1px solid var(--border)') + ';background:' + (isActive ? 'rgba(227,30,36,.06)' : 'var(--surface)') + ';color:#fff;cursor:pointer;font-family:Inter,sans-serif;font-size:14px;font-weight:600;transition:all .15s">'
                    + '<span style="font-size:24px">' + l.flag + '</span>'
                    + '<span style="flex:1;text-align:left">' + l.name + '</span>'
                    + (isActive ? '<span class="material-symbols-outlined" style="color:var(--red);font-size:20px">check_circle</span>' : '')
                    + '</button>';
            }).join('');
            ol.onclick = function (e) { if (e.target === ol) ol.style.display = 'none' };
        }

        function setLanguage(code) {
            /* Save via API and reload */
            fetch(API + '/api/set-language', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(Object.assign({}, auth(), { language: code })) })
                .then(function () {
                    /* Reload page with new lang */
                    var params = new URLSearchParams(location.search);
                    params.set('lang', code);
                    location.search = params.toString();
                }).catch(function () {
                    var params = new URLSearchParams(location.search);
                    params.set('lang', code);
                    location.search = params.toString();
                });
        }

        function initLangDisplay() {
            var cur = LANG_OPTIONS[LANG];
            var el = document.getElementById('profLangCurrent');
            if (el && cur) el.textContent = cur.flag + ' ' + cur.name;
            var el2 = document.getElementById('profLang');
            if (el2) el2.textContent = LANG === 'ru' ? 'Язык' : LANG === 'ua' ? 'Мова' : LANG === 'pl' ? 'Język' : 'Language';
        }

        /* === CRASH GAME LOGIC === */
        let crashState = 'idle'; // idle, betting, running, cashed_out, crashed
        let crashSocket = null;
        let crashTimer = null;
        let crashGraphTimer = null;
        let currentMult = 1.00;
        let myBet = 0;
        let myCashout = 0;

        function initCrashCanvas() {
            const canvas = document.getElementById('crashCanvas');
            const parent = canvas.parentElement;
            canvas.width = parent.clientWidth;
            canvas.height = parent.clientHeight;
            drawCrashGraph(0);
        }
        window.addEventListener('resize', initCrashCanvas);

        function drawCrashGraph(progress) { // progress 0 to 1
            const canvas = document.getElementById('crashCanvas');
            const ctx = canvas.getContext('2d');
            const w = canvas.width;
            const h = canvas.height;

            ctx.clearRect(0, 0, w, h);

            ctx.strokeStyle = 'rgba(255,255,255,0.05)';
            ctx.lineWidth = 1;
            ctx.beginPath();
            for (let i = 0; i < 5; i++) {
                ctx.moveTo(0, i * h / 5);
                ctx.lineTo(w, i * h / 5);
                ctx.moveTo(i * w / 5, 0);
                ctx.lineTo(i * w / 5, h);
            }
            ctx.stroke();

            if (currentMult > 1.00) {
                ctx.beginPath();
                ctx.moveTo(0, h);
                const x = w * progress;
                const y = h - (h * Math.pow(progress, 2));

                ctx.quadraticCurveTo(x * 0.5, h, x, y);

                ctx.strokeStyle = crashState === 'crashed' ? '#E31E24' : '#22C55E';
                ctx.lineWidth = 4;
                ctx.lineCap = 'round';
                ctx.stroke();

                ctx.shadowColor = crashState === 'crashed' ? 'rgba(227,30,36,0.5)' : 'rgba(34,197,94,0.5)';
                ctx.shadowBlur = 10;
                ctx.stroke();
                ctx.shadowBlur = 0;

                ctx.beginPath();
                ctx.arc(x, y, 6, 0, Math.PI * 2);
                ctx.fillStyle = crashState === 'crashed' ? '#E31E24' : '#22C55E';
                ctx.fill();
            }
        }

        function playCrashLoop() {
            const crashPoint = Math.max(1.00, (100 / (Math.random() * 100)) * 0.99).toFixed(2);
            let targetMult = parseFloat(crashPoint);
            if (Math.random() < 0.2) targetMult = 1.00;

            let t = 0;
            const tick = 50;
            const totalDuration = targetMult < 1.1 ? 500 : 2000 + (targetMult * 100);

            crashState = 'running';
            document.getElementById('crashMult').classList.remove('crashed');
            document.getElementById('crashMult').classList.add('active');

            let btn = document.getElementById('crashBtn');
            if (myBet > 0 && myCashout === 0) {
                btn.className = 'crash-action-btn cashout';
                btn.innerHTML = 'CASHOUT<br><span class="crash-action-sub">...</span>';
            } else if (myBet === 0) {
                btn.className = 'crash-action-btn wait';
                btn.innerHTML = 'WAITING<br><span class="crash-action-sub">Round in progress</span>';
            }

            crashGraphTimer = setInterval(() => {
                t += tick;
                let progress = Math.min(1, t / totalDuration);

                currentMult = 1.00 + (targetMult - 1.00) * Math.pow(progress, 3);

                document.getElementById('crashMult').textContent = currentMult.toFixed(2) + 'x';
                drawCrashGraph(progress);

                if (myBet > 0 && myCashout === 0) {
                    let w = (myBet * currentMult).toFixed(2);
                    btn.innerHTML = 'CASHOUT<br><span class="crash-action-sub">' + w + ' 🪙</span>';

                    let autoVal = parseFloat(document.getElementById('crashAutoCashout').value);
                    if (autoVal > 1.00 && currentMult >= autoVal) {
                        doCashout(autoVal);
                    }
                }

                if (progress >= 1) {
                    clearInterval(crashGraphTimer);
                    triggerCrash(targetMult);
                }
            }, tick);
        }

        function triggerCrash(finalMult) {
            crashState = 'crashed';
            document.getElementById('crashMult').textContent = finalMult.toFixed(2) + 'x';
            document.getElementById('crashMult').classList.remove('active');
            document.getElementById('crashMult').classList.add('crashed');
            drawCrashGraph(1);

            if (myBet > 0 && myCashout === 0) {
                myBet = 0;
            }

            const p = document.createElement('div');
            p.className = 'ch-pill ' + (finalMult >= 2.0 ? 'high' : 'low');
            p.textContent = finalMult.toFixed(2) + 'x';
            const hist = document.getElementById('crashHistory');
            hist.insertBefore(p, hist.firstChild);
            if (hist.children.length > 20) hist.removeChild(hist.lastChild);

            let btn = document.getElementById('crashBtn');
            btn.className = 'crash-action-btn wait';
            btn.innerHTML = 'CRASHED<br><span class="crash-action-sub">Next round starting soon</span>';

            setTimeout(() => {
                myBet = 0;
                myCashout = 0;
                currentMult = 1.00;
                crashState = 'idle';
                document.getElementById('crashMult').classList.remove('crashed');
                document.getElementById('crashMult').textContent = '1.00x';
                document.getElementById('crashProfit').classList.remove('show');
                const canvas = document.getElementById('crashCanvas');
                canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
                drawCrashGraph(0);

                btn.className = 'crash-action-btn bet';
                btn.innerHTML = 'BET<br><span class="crash-action-sub">Next Round</span>';
            }, 3000);
        }

        function crashAction() {
            let btn = document.getElementById('crashBtn');
            if (crashState === 'idle') {
                let betAmt = parseFloat(document.getElementById('crashBetAmount').value);
                if (betAmt <= 0) return;

                let activeBal = activeWallet === 'stars' ? starsBalance : (usdtBalance * 100);
                if (betAmt > activeBal) {
                    return; // silently return, not enough funds
                }

                if (activeWallet === 'stars') starsBalance -= betAmt;
                else usdtBalance -= (betAmt / 100);
                updateBalanceUI();

                myBet = betAmt;
                btn.className = 'crash-action-btn cancel';
                btn.innerHTML = 'CANCEL<br><span class="crash-action-sub">Waiting for round</span>';

                setTimeout(playCrashLoop, 1000);
                crashState = 'betting';

            } else if (crashState === 'betting') {
                if (activeWallet === 'stars') starsBalance += myBet;
                else usdtBalance += (myBet / 100);
                updateBalanceUI();

                myBet = 0;
                btn.className = 'crash-action-btn bet';
                btn.innerHTML = 'BET<br><span class="crash-action-sub">Next Round</span>';

            } else if (crashState === 'running' && myBet > 0 && myCashout === 0) {
                doCashout(currentMult);
            }
        }

        function doCashout(mult) {
            myCashout = (myBet * mult).toFixed(2);
            let winToken = activeWallet === 'stars' ? '⭐' : '🪙';

            if (activeWallet === 'stars') starsBalance += parseFloat(myCashout);
            else usdtBalance += (parseFloat(myCashout) / 100);
            updateBalanceUI();

            let profitEl = document.getElementById('crashProfit');
            profitEl.textContent = 'Profit: +' + myCashout + ' ' + winToken;
            profitEl.classList.add('show');

            let btn = document.getElementById('crashBtn');
            btn.className = 'crash-action-btn wait';
            btn.innerHTML = 'CASHED OUT<br><span class="crash-action-sub">' + mult.toFixed(2) + 'x</span>';
        }

        const oldUpdateBalanceUI = updateBalanceUI;
        updateBalanceUI = function () {
            oldUpdateBalanceUI();
            let cb = document.getElementById('crashBal');
            if (cb) {
                cb.textContent = activeWallet === 'stars' ? starsBalance + ' ⭐' : (usdtBalance !== null ? (usdtBalance * 100).toFixed(2) : '0');
            }
        };

        const oldNav = nav;
        nav = function (screen) {
            oldNav(screen);
            if (screen === 'crash') {
                setTimeout(initCrashCanvas, 100);
            }
        }

        function initLangDisplay() {
            var el = document.getElementById('profLangCurrent');
            if (el) el.textContent = LANG.toUpperCase();
        }

        /* === INIT === */
        if (window.Telegram && window.Telegram.WebApp) {
            const tg = window.Telegram.WebApp;
            tg.ready();

            // Fullsize mode (like BotFather) — expand + requestFullscreen
            const ensureExpand = () => {
                tg.expand();
                if (tg.isExpanded === false) {
                    setTimeout(ensureExpand, 200);
                }
            };
            ensureExpand();

            // Request fullscreen for fullsize experience on modern Telegram clients
            // This makes the app fill the entire screen like BotFather mini-apps
            if (tg.requestFullscreen) {
                try { tg.requestFullscreen(); } catch (e) { }
            }

            // Apply Telegram safe area insets for fullscreen mode
            function applyTgSafeArea() {
                var csa = tg.contentSafeAreaInset || {};
                var sa = tg.safeAreaInset || {};
                var topInset = (sa.top || 0) + (csa.top || 0);
                if (topInset > 0) {
                    document.documentElement.style.setProperty('--tg-safe-top', topInset + 'px');
                }
            }
            applyTgSafeArea();
            tg.onEvent('contentSafeAreaChanged', applyTgSafeArea);
            tg.onEvent('safeAreaChanged', applyTgSafeArea);

            tg.enableClosingConfirmation();
            tg.setHeaderColor('#000000');
            tg.setBackgroundColor('#121212');
        }
        initLocale();
        initLangDisplay();
        buildCategories();
        buildProviders();
        buildGameGrid();
        initBonuses();
        buildWalletPackages();
        loadBalance();
        checkWheel();
        loadTopWinnings('day');
        updateBonusBadge();
        buildLiveDrops();
        loadReferral();
    </script>
</body>

</html>
