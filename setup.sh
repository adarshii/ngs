#!/bin/bash
# NGS Pipeline - Comprehensive Setup Script
# Automated setup of environment, dependencies, and directory structure
# Usage: bash setup.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check requirements
check_requirements() {
    print_header "Checking Requirements"

    # Check conda
    if ! command -v conda &> /dev/null; then
        print_error "Conda not found. Please install Miniconda/Anaconda."
        exit 1
    fi
    print_success "Conda found: $(conda --version)"

    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found"
        exit 1
    fi
    print_success "Python 3 found: $(python3 --version)"

    # Check git
    if ! command -v git &> /dev/null; then
        print_warning "Git not found (optional)"
    else
        print_success "Git found: $(git --version)"
    fi
}

# Create directory structure
create_directories() {
    print_header "Creating Directory Structure"

    mkdir -p data/raw_data
    mkdir -p data/reference
    mkdir -p data/trimmed
    mkdir -p results/fastqc
    mkdir -p results/aligned
    mkdir -p results/variants
    mkdir -p results/annotated
    mkdir -p results/reports
    mkdir -p results/logs
    mkdir -p config
    mkdir -p scripts
    mkdir -p docs

    print_success "Directory structure created"
}

# Create conda environment
create_environment() {
    print_header "Creating Conda Environment"

    # Check if environment already exists
    if conda env list | grep -q ngs-wgs; then
        print_warning "Environment 'ngs-wgs' already exists"
        read -p "Do you want to reinstall it? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_header "Removing Old Environment"
            conda env remove -n ngs-wgs -y
        else
            print_success "Keeping existing environment"
            return
        fi
    fi

    # Create environment from file
    if [ -f "environment.yaml" ]; then
        print_header "Creating Environment from environment.yaml"
        conda env create -f environment.yaml -y
        print_success "Conda environment created: ngs-wgs"
    else
        print_error "environment.yaml not found"
        exit 1
    fi
}

# Validate configuration
validate_configuration() {
    print_header "Validating Configuration"

    if [ ! -f "config/config.yaml" ]; then
        print_error "config/config.yaml not found"
        exit 1
    fi
    print_success "config/config.yaml found"

    if [ ! -f "config/samples.tsv" ]; then
        print_warning "config/samples.tsv not found (will be created)"
        touch config/samples.tsv
    fi
    print_success "config/samples.tsv exists"

    if [ ! -f "Snakefile" ]; then
        print_error "Snakefile not found"
        exit 1
    fi
    print_success "Snakefile found"
}

# Create sample template
create_sample_template() {
    print_header "Creating Sample Sheet Template"

    if [ ! -s "config/samples.tsv" ]; then
        cat > config/samples.tsv << 'EOF'
# NGS Pipeline Sample Sheet
# Fields: sample_id, read1_path, read2_path, platform, sample_name
# Example:
# sample1    data/raw_data/s1_R1.fastq.gz    data/raw_data/s1_R2.fastq.gz    ILLUMINA    S001

EOF
        print_success "Sample template created"
    else
        print_warning "config/samples.tsv already has content"
    fi
}

# Create .gitignore
create_gitignore() {
    print_header "Creating .gitignore"

    if [ ! -f ".gitignore" ]; then
        cat > .gitignore << 'EOF'
# Data files
data/raw_data/*.fastq
data/raw_data/*.fastq.gz
data/reference/
data/trimmed/

# Results
results/
logs/
.snakemake/

# Python
__pycache__/
*.py[cod]
*.egg-info/
.pytest_cache/

# System
.DS_Store
*.swp
*.swo
*~
.env

# IDE
.vscode/
.idea/
*.sublime-project
*.sublime-workspace

# Conda
envs/
EOF
        print_success ".gitignore created"
    fi
}

# Set permissions
set_permissions() {
    print_header "Setting Permissions"

    chmod +x scripts/*.sh
    print_success "Script permissions set"
}

# Print summary
print_summary() {
    print_header "Setup Complete! 🎉"

    echo -e "\n${GREEN}Next Steps:${NC}"
    echo "1. Activate the environment:"
    echo -e "   ${BLUE}conda activate ngs-wgs${NC}"
    echo ""
    echo "2. Download and prepare reference genome (first time only):"
    echo -e "   ${BLUE}bash scripts/prepare_reference.sh${NC}"
    echo ""
    echo "3. Add your FASTQ files to data/raw_data/"
    echo ""
    echo "4. Create sample sheet (edit config/samples.tsv):"
    echo -e "   ${BLUE}nano config/samples.tsv${NC}"
    echo ""
    echo "5. Run the pipeline:"
    echo -e "   ${BLUE}snakemake -j 8 --configfile config/config.yaml${NC}"
    echo ""
    echo -e "${GREEN}Documentation:${NC}"
    echo "  - EXECUTION_GUIDE.md    : How to run the pipeline"
    echo "  - PROJECT_OVERVIEW.md   : Complete project summary"
    echo "  - docs/TUTORIAL.md      : Detailed step-by-step guide"
    echo ""
    echo -e "${GREEN}Repository:${NC}"
    echo "  - https://github.com/adarshii/ngs"
    echo ""
}

# Main execution
main() {
    clear
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════╗"
    echo "║  NGS WGS Variant-Calling Pipeline     ║"
    echo "║  Automated Setup Script               ║"
    echo "╚════════════════════════════════════════╝"
    echo -e "${NC}\n"

    check_requirements
    create_directories
    create_environment
    validate_configuration
    create_sample_template
    create_gitignore
    set_permissions
    print_summary
}

# Run main
main
