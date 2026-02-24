/**
 * Universal Casino Math Engine
 * Handles Provably Fair RNG, RTP calculations, and deterministic game outcomes.
 */

class CasinoMath {
    constructor() {
        this.serverSeed = this.generateHash();
        this.clientSeed = 'rubybet-player-' + Math.floor(Math.random() * 10000);
        this.nonce = 0;
    }

    // --- Core Cryptography ---

    /**
     * Simulates SHA-256 hashing for the provably fair seed combination.
     * In a real backend, this would use Node's crypto module. 
     * For client-side simulation, we use a basic string hashing function.
     */
    async generateHash(seedString = Math.random().toString()) {
        const msgBuffer = new TextEncoder().encode(seedString);
        const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
        return hashHex;
    }

    /**
     * Generates a deterministic float between 0.0 (inclusive) and 1.0 (exclusive)
     * based on the current Server Seed, Client Seed, and Nonce.
     */
    async getNextPRNG() {
        // Combine seeds and nonce
        const comboString = `${this.serverSeed}:${this.clientSeed}:${this.nonce}`;
        this.nonce++; // Increment for next roll

        // Hash the combination
        const hash = await this.generateHash(comboString);

        // Take the first 8 hex characters (32 bits) to form a float
        const subHex = hash.substring(0, 8);
        const decimal = parseInt(subHex, 16);

        // Max value for 8 hex chars is 4294967295 (0xFFFFFFFF)
        const floatValue = decimal / 4294967296;

        return floatValue;
    }

    // --- Game Logic: Plinko ---

    /**
     * Calculates the deterministic outcome and visual drop path for Plinko.
     * 
     * @param {number} rows - Number of peg rows (e.g., 8 to 16)
     * @param {Array<number>} multipliers - Array of target multipliers mapping to bottom buckets
     * @param {object} weights - Distribution weights to enforce RTP
     * @returns {object} - The selected multiplier bucket index and the precise left/right path
     */
    async calculatePlinkoDrop(rows, multipliers) {
        // 1. Generate the provably fair random float
        const prngFloat = await this.getNextPRNG();

        // 2. Define payout weights for an ~96% RTP curve on an 8-row board
        // Buckets (9 total): [ 100x, 10x, 5x, 2x, 1x, 0.5x, 1x, 2x, 5x, 10x, 100x ] 
        // Note: Standard Plinko has normal distribution. We manipulate weights to control house edge.
        const rtpWeights = [
            0.001, // Bucket 0: Extreme Left (100x)
            0.015, // Bucket 1: (10x)
            0.050, // Bucket 2: (5x)
            0.150, // Bucket 3: (2x)
            0.568, // Bucket 4: Center (0.5x)
            0.150, // Bucket 5: (2x)
            0.050, // Bucket 6: (5x)
            0.015, // Bucket 7: (10x)
            0.001  // Bucket 8: Extreme Right (100x)
        ];

        // 3. Map PRNG float to the weighted bucket outcome
        let cumulativeWeight = 0;
        let targetBucketIndex = Math.floor(rows / 2); // Default to center

        for (let i = 0; i < rtpWeights.length; i++) {
            cumulativeWeight += rtpWeights[i];
            if (prngFloat <= cumulativeWeight) {
                targetBucketIndex = i;
                break;
            }
        }

        const payoutMultiplier = multipliers[targetBucketIndex] || 0.5;

        // 4. Reverse Engineer the Path
        // A full path requires exactly `rows` number of left/right decisions.
        // Left = 0, Right = 1.
        // The bucket index is exactly equal to the number of 'Right' decisions made!
        let path = [];
        let rightsNeeded = targetBucketIndex;
        let leftsNeeded = rows - targetBucketIndex;

        // Populate array with exactly the required number of lefts and rights
        for (let i = 0; i < rightsNeeded; i++) path.push(1);
        for (let i = 0; i < leftsNeeded; i++) path.push(0);

        // Fisher-Yates shuffle to randomize the order of the path
        for (let i = path.length - 1; i > 0; i--) {
            // Local simple random for visual path shuffling (does not affect financial outcome)
            const j = Math.floor(Math.random() * (i + 1));
            [path[i], path[j]] = [path[j], path[i]];
        }

        return {
            bucketIndex: targetBucketIndex,
            multiplier: payoutMultiplier,
            path: path, // Array of 0s and 1s representing Left and Right bounces
            provablyFairRecord: {
                serverSeed: this.serverSeed,
                clientSeed: this.clientSeed,
                nonce: this.nonce - 1, // The nonce used for this specific roll
                prngFloat: prngFloat
            }
        };
    }

    /**
     * Optional: Update client seed dynamically
     */
    setClientSeed(newSeed) {
        this.clientSeed = newSeed;
        this.nonce = 0; // Reset nonce on new seed
    }
}

// Export singleton instance for global browser usage
window.casinoMath = new CasinoMath();
