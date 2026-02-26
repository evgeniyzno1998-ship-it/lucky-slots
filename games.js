function getGamesConfig(T) {
    T = T || {};
    return [
        {
            id: 'ruby_slots', name: T.slotName || 'Ruby Slots',
            emoji: '🎰', icon: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDaEolN36F7I9DO5xzDpZJT44gKy0UqcrJkYSpxyvjhw60tyAD7Gy1Bh8-CCjn0wUqGk1dsU3gdG_wlCSodYaiglPb9p8QgUqGUehCxqDwVJx93ersDjvbFa3lgxVwIN2gd29K0ZxblLEP1EkgNZjgTh-fyy3QTKfOvEz8y3gytYBMe2jAJiNryHDsJPpexYxJRkJes_Fb1dmeQ8JqtUOssDqpIUiDNtFwWXyXoN3at4S1zDC3DhMbXR_TZYjG8VkEpKZFQ2t4ucw',
            tag: T.slotTag || 'POPULAR', screen: 'game', bg: '#ff416c', provider: 'rubybet'
        },
        {
            id: 'crash', name: T.crashName || 'Crash',
            emoji: '📈', icon: '',
            tag: T.hot || 'HOT', screen: 'crash', bg: '#38ef7d', provider: 'rubybet'
        },
        {
            id: 'dice', name: T.diceName || 'Ruby Dice',
            emoji: '🎲', icon: '',
            tag: T.comingTag || 'SOON', screen: null, bg: '#4A00E0', provider: 'rubybet'
        },
        {
            id: 'mines', name: T.mineName || 'Mines',
            emoji: '💣', icon: '',
            tag: T.comingTag || 'SOON', screen: null, bg: '#1565C0', provider: 'rubybet'
        },
        {
            id: 'plinko', name: 'Galactic Plinko',
            emoji: '🚀', icon: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAV67NDOkqHDYuJOwD9Je6tBpmvW3RSI4HF0XkpQdgV_iaaVZYQdnLiQU89PymnRn5IxYBRn0BekcKrZ7NHIYjIugI9wO6OBWtjh95WkV_gWTsuQYmVQBUUNzx_4PBG6K0GmTJ0X4UIHtuR-300bhj-NrT24I4jFK3PVoXbEiArjjbMMNC2Z1gegewHMhPAo6Jv8jx7YoLzIBfS7qP7BZW6Egl5S2nvhVfyUlcT7IWmtAyp3Nmk9-kJ1ey0wszCI9yv8Z5gVji0xsQ',
            tag: 'NEW', screen: 'plinko', bg: '#e42127', provider: 'rubybet', category: 'plinko'
        },
        { id: 'roulette', name: 'Roulette', emoji: '🎡', tag: 'SOON', screen: null, bg: '#ef4444', provider: 'evolution' },
        { id: 'blackjack', name: 'Blackjack', emoji: '🃏', tag: 'SOON', screen: null, bg: '#10b981', provider: 'evolution' },
        { id: 'sweet_bonanza', name: 'Sweet Bonanza', emoji: '🍬', tag: 'SOON', screen: null, bg: '#ec4899', provider: 'pragmatic' },
        { id: 'gates_olympus', name: 'Gates of Olympus', emoji: '⚡', tag: 'SOON', screen: null, bg: '#6366f1', provider: 'pragmatic' },
        { id: 'big_bass', name: 'Big Bass Bonanza', emoji: '🐟', tag: 'SOON', screen: null, bg: '#14b8a6', provider: 'pragmatic' },
        { id: 'starlight', name: 'Starlight Princess', emoji: '👸', tag: 'SOON', screen: null, bg: '#8b5cf6', provider: 'pgsoft' },
        { id: 'wanted', name: 'Wanted Dead or Wild', emoji: '🤠', tag: 'SOON', screen: null, bg: '#b92b27', provider: 'hacksaw' }
    ];
}
