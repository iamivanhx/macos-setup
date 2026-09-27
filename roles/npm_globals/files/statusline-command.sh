#!/bin/bash
# Claude Code status line
# Single-line, truecolor status line: repo | branch | context bar | cost | velocity | model

input=$(cat)

model_name=$(echo "$input" | jq -r '.model.display_name // "model"')
effort=$(echo "$input" | jq -r '.effort.level // empty')
cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // "."')

repo_name=$(echo "$input" | jq -r '.workspace.repo.name // empty')
if [ -z "$repo_name" ]; then
  repo_name=$(basename "$cwd")
fi

branch=$(git -C "$cwd" --no-optional-locks branch --show-current 2>/dev/null)

used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // 0')
used_int=$(printf '%.0f' "$used_pct" 2>/dev/null || echo 0)

cost=$(echo "$input" | jq -r '.cost.total_cost_usd // 0')
cost_fmt=$(printf '%.2f' "$cost" 2>/dev/null || echo "0.00")
lines_added=$(echo "$input" | jq -r '.cost.total_lines_added // 0')
lines_removed=$(echo "$input" | jq -r '.cost.total_lines_removed // 0')

# --- color helpers -----------------------------------------------------
rgb() { printf '\033[38;2;%d;%d;%dm' "$1" "$2" "$3"; }
RESET=$'\033[0m'
BOLD=$'\033[1m'
DIM=$'\033[2m'

# Gradient across green(0,200,80) -> yellow(220,200,0) -> red(220,40,20)
gradient_color() {
  local pct=$1 t r g b
  if [ "$pct" -le 50 ]; then
    t=$(awk "BEGIN{print $pct/50}")
    r=$(awk "BEGIN{printf \"%d\", 0 + (220-0)*$t}")
    g=200
    b=$(awk "BEGIN{printf \"%d\", 80 + (0-80)*$t}")
  else
    t=$(awk "BEGIN{print ($pct-50)/50}")
    r=220
    g=$(awk "BEGIN{printf \"%d\", 200 + (40-200)*$t}")
    b=$(awk "BEGIN{printf \"%d\", 0 + (20-0)*$t}")
  fi
  echo "$r $g $b"
}

SEP="${DIM}$(rgb 120 120 120) | ${RESET}"

# --- 20-block context bar ----------------------------------------------
filled=$(( used_int * 20 / 100 ))
[ "$filled" -gt 20 ] && filled=20

bar=""
for i in $(seq 1 20); do
  if [ "$i" -le "$filled" ]; then
    block_pct=$(( i * 100 / 20 ))
    read -r br bg bb <<EOF
$(gradient_color "$block_pct")
EOF
    bar="${bar}$(rgb "$br" "$bg" "$bb")█"
  else
    bar="${bar}$(rgb 60 60 60)█"
  fi
done
bar="${bar}${RESET}"

# --- dynamic emoji + percentage color -----------------------------------
if [ "$used_int" -lt 20 ]; then
  emoji="🟢"
elif [ "$used_int" -lt 70 ]; then
  emoji="⚡"
elif [ "$used_int" -lt 90 ]; then
  emoji="🔥"
else
  emoji="🚨"
fi

read -r pr pg pb <<EOF
$(gradient_color "$used_int")
EOF
pct_color="$(rgb "$pr" "$pg" "$pb")"

# --- assemble segments ----------------------------------------------------
repo_seg="${BOLD}$(rgb 220 200 0)${repo_name}${RESET}"

branch_seg=""
if [ -n "$branch" ]; then
  branch_seg="${SEP}${BOLD}$(rgb 0 200 200)🌿 (${branch})${RESET}"
fi

context_seg="${SEP}${bar} ${pct_color}${emoji} ${used_int}%${RESET}"

cost_seg="${SEP}$(rgb 255 200 0)\$${cost_fmt}${RESET}"

velocity_seg="${SEP}$(rgb 0 200 80)+${lines_added}${RESET} $(rgb 220 40 20)-${lines_removed}${RESET}"

model_str="🤖 ${model_name}"
if [ -n "$effort" ]; then
  model_str="${model_str} (${effort})"
fi
model_seg="${SEP}$(rgb 200 80 220)${model_str}${RESET}"

printf '%s' "${repo_seg}${branch_seg}${context_seg}${cost_seg}${velocity_seg}${model_seg}"
