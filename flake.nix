# clash_testbench
# Sébastien Deriaz
# 29.12.2022

{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-22.11";
    flake-utils.url = "github:numtide/flake-utils";
    nix-filter.url = "github:numtide/nix-filter";
    flake-compat = {
      url = "github:edolstra/flake-compat";
      flake = false;
    };
  };

  outputs = inputs: inputs.flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = import inputs.nixpkgs {
        inherit system;
        overlays = [
          inputs.nix-filter.overlays.default
        ];
        config.allowUnfree = true;
      };
    in
    {
      inherit pkgs;

      devShells.default = pkgs.mkShell {
        nativeBuildInputs = with pkgs; [
          
          (haskellPackages.ghcWithPackages (ps: with ps; [
            clash-ghc
            ghc-typelits-extra
            ghc-typelits-knownnat
            ghc-typelits-natnormalise
          ]))
        ];
      };
    });
}
