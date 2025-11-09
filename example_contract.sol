// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title PublicDomainMovieNFT
 * @dev NFT contract for minting public domain movie frames and audio assets
 *
 * This contract is designed for the Anna Maria Pierangeli project
 * to mint NFTs from public domain films.
 *
 * Features:
 * - ERC-721 standard compliance
 * - URI storage for IPFS metadata
 * - Owner-controlled minting
 * - Token counter for sequential IDs
 * - Enumerable for collection browsing
 */
contract PublicDomainMovieNFT is ERC721URIStorage, Ownable {
    using Counters for Counters.Counter;

    // Token ID counter
    Counters.Counter private _tokenIds;

    // Movie information
    struct MovieInfo {
        string title;
        uint16 year;
        string director;
        string publicDomainReason;
    }

    // Token to movie mapping
    mapping(uint256 => string) private _tokenToMovie;

    // Movie catalog
    mapping(string => MovieInfo) public movies;

    // Total minted per movie
    mapping(string => uint256) public movieTotalSupply;

    // Events
    event MovieRegistered(string movieId, string title, uint16 year);
    event FrameMinted(uint256 indexed tokenId, string movieId, uint256 frameNumber);
    event AudioMinted(uint256 indexed tokenId, string movieId, string assetType);

    /**
     * @dev Constructor
     * @param initialOwner Address of the contract owner (your wallet)
     */
    constructor(address initialOwner)
        ERC721("Public Domain Movie Collection", "PDMC")
        Ownable(initialOwner)
    {}

    /**
     * @dev Register a movie in the contract
     * @param movieId Unique identifier for the movie (e.g., "night-of-living-dead")
     * @param title Full title of the movie
     * @param year Year of release
     * @param director Director's name
     * @param publicDomainReason Why the movie is in public domain
     */
    function registerMovie(
        string memory movieId,
        string memory title,
        uint16 year,
        string memory director,
        string memory publicDomainReason
    ) external onlyOwner {
        movies[movieId] = MovieInfo({
            title: title,
            year: year,
            director: director,
            publicDomainReason: publicDomainReason
        });

        emit MovieRegistered(movieId, title, year);
    }

    /**
     * @dev Mint a single NFT
     * @param to Address to receive the NFT
     * @param tokenURI IPFS URI for the metadata (ipfs://...)
     * @return tokenId The ID of the newly minted token
     */
    function mint(address to, string memory tokenURI)
        public
        onlyOwner
        returns (uint256)
    {
        _tokenIds.increment();
        uint256 newTokenId = _tokenIds.current();

        _mint(to, newTokenId);
        _setTokenURI(newTokenId, tokenURI);

        return newTokenId;
    }

    /**
     * @dev Mint a frame NFT with movie association
     * @param to Address to receive the NFT
     * @param tokenURI IPFS URI for the metadata
     * @param movieId Movie identifier
     * @param frameNumber Frame number in the movie
     * @return tokenId The ID of the newly minted token
     */
    function mintFrame(
        address to,
        string memory tokenURI,
        string memory movieId,
        uint256 frameNumber
    ) external onlyOwner returns (uint256) {
        uint256 tokenId = mint(to, tokenURI);

        _tokenToMovie[tokenId] = movieId;
        movieTotalSupply[movieId]++;

        emit FrameMinted(tokenId, movieId, frameNumber);

        return tokenId;
    }

    /**
     * @dev Mint an audio NFT with movie association
     * @param to Address to receive the NFT
     * @param tokenURI IPFS URI for the metadata
     * @param movieId Movie identifier
     * @param assetType Type of audio asset (e.g., "full", "segment")
     * @return tokenId The ID of the newly minted token
     */
    function mintAudio(
        address to,
        string memory tokenURI,
        string memory movieId,
        string memory assetType
    ) external onlyOwner returns (uint256) {
        uint256 tokenId = mint(to, tokenURI);

        _tokenToMovie[tokenId] = movieId;
        movieTotalSupply[movieId]++;

        emit AudioMinted(tokenId, movieId, assetType);

        return tokenId;
    }

    /**
     * @dev Batch mint multiple NFTs
     * @param to Address to receive the NFTs
     * @param tokenURIs Array of IPFS URIs
     * @return tokenIds Array of newly minted token IDs
     */
    function batchMint(address to, string[] memory tokenURIs)
        external
        onlyOwner
        returns (uint256[] memory)
    {
        uint256[] memory tokenIds = new uint256[](tokenURIs.length);

        for (uint256 i = 0; i < tokenURIs.length; i++) {
            tokenIds[i] = mint(to, tokenURIs[i]);
        }

        return tokenIds;
    }

    /**
     * @dev Get total number of tokens minted
     * @return Total supply
     */
    function totalSupply() external view returns (uint256) {
        return _tokenIds.current();
    }

    /**
     * @dev Get movie associated with a token
     * @param tokenId Token ID
     * @return Movie ID
     */
    function getTokenMovie(uint256 tokenId) external view returns (string memory) {
        require(_ownerOf(tokenId) != address(0), "Token does not exist");
        return _tokenToMovie[tokenId];
    }

    /**
     * @dev Get movie information
     * @param movieId Movie identifier
     * @return title, year, director, publicDomainReason
     */
    function getMovieInfo(string memory movieId)
        external
        view
        returns (
            string memory title,
            uint16 year,
            string memory director,
            string memory publicDomainReason
        )
    {
        MovieInfo memory movie = movies[movieId];
        return (movie.title, movie.year, movie.director, movie.publicDomainReason);
    }

    /**
     * @dev Check if contract supports an interface
     * @param interfaceId Interface identifier
     * @return bool True if supported
     */
    function supportsInterface(bytes4 interfaceId)
        public
        view
        virtual
        override(ERC721URIStorage)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}

/**
 * DEPLOYMENT INSTRUCTIONS:
 *
 * 1. Using Remix IDE (https://remix.ethereum.org/):
 *    - Copy this code to a new file
 *    - Compile with Solidity 0.8.20+
 *    - Select "Injected Provider - MetaMask"
 *    - Deploy with your wallet address as initialOwner
 *
 * 2. Using Hardhat:
 *    - npx hardhat compile
 *    - npx hardhat run scripts/deploy.js --network polygon_mumbai
 *
 * 3. Networks to deploy to:
 *    - Polygon Mumbai (testnet): Free testing
 *    - Polygon Mainnet: Production (~$0.003 per NFT)
 *    - Ethereum Sepolia (testnet): Free testing
 *    - Ethereum Mainnet: Production (~$5-50 per NFT)
 *
 * 4. After deployment:
 *    - Note the contract address
 *    - Export the ABI to contract_abi.json
 *    - Add contract address to .env
 *    - Register your movies using registerMovie()
 *
 * 5. Verify contract on block explorer:
 *    - Polygonscan: https://mumbai.polygonscan.com/ (testnet)
 *    - Etherscan: https://sepolia.etherscan.io/ (testnet)
 *
 * EXAMPLE REGISTRATION:
 *
 * await contract.registerMovie(
 *   "night-of-living-dead",
 *   "Night of the Living Dead",
 *   1968,
 *   "George A. Romero",
 *   "Copyright notice omission"
 * );
 *
 * GAS COSTS (Polygon Mumbai - Testnet):
 * - Deployment: FREE (testnet MATIC from faucet)
 * - Register movie: FREE
 * - Mint single NFT: FREE
 * - Mint 10 NFTs: FREE
 *
 * GAS COSTS (Polygon Mainnet):
 * - Deployment: ~$0.50
 * - Register movie: ~$0.01
 * - Mint single NFT: ~$0.003
 * - Mint 100,000 NFTs: ~$300-400
 *
 * SECURITY:
 * - Only owner can mint
 * - Use multi-sig for mainnet
 * - Test thoroughly on testnet first
 * - Verify contract code on explorer
 */
