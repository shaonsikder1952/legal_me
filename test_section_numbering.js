// Test script to verify dynamic section numbering logic
function testSectionNumbering() {
  // Simulate the dynamic section numbering logic
  let sectionNumber = 0;
  const getNextSectionNumber = () => ++sectionNumber;
  
  console.log("Testing dynamic section numbering:");
  
  // Always visible sections
  console.log(`Section ${getNextSectionNumber()}: Document Overview`);
  console.log(`Section ${getNextSectionNumber()}: Summary`);
  
  // Conditional sections (simulate different scenarios)
  
  // Scenario 1: All conditional sections are visible
  console.log("\nScenario 1: All sections visible");
  sectionNumber = 2; // Reset after first 2 sections
  const hasSafeClauses = true;
  const hasAttentionClauses = true;
  const hasViolationClauses = true;
  const hasKeyExcerpts = true;
  
  if (hasSafeClauses) {
    console.log(`Section ${getNextSectionNumber()}: Clauses That Are Acceptable`);
  }
  if (hasAttentionClauses) {
    console.log(`Section ${getNextSectionNumber()}: Clauses That May Be Problematic`);
  }
  if (hasViolationClauses) {
    console.log(`Section ${getNextSectionNumber()}: Clauses That Violate German Law`);
  }
  console.log(`Section ${getNextSectionNumber()}: Recommendations`);
  if (hasKeyExcerpts) {
    console.log(`Section ${getNextSectionNumber()}: Key Excerpts from Document`);
  }
  
  // Scenario 2: Only some conditional sections are visible
  console.log("\nScenario 2: Only some conditional sections visible");
  sectionNumber = 2; // Reset after first 2 sections
  const hasSafeClauses2 = false;
  const hasAttentionClauses2 = true;
  const hasViolationClauses2 = false;
  const hasKeyExcerpts2 = true;
  
  if (hasSafeClauses2) {
    console.log(`Section ${getNextSectionNumber()}: Clauses That Are Acceptable`);
  }
  if (hasAttentionClauses2) {
    console.log(`Section ${getNextSectionNumber()}: Clauses That May Be Problematic`);
  }
  if (hasViolationClauses2) {
    console.log(`Section ${getNextSectionNumber()}: Clauses That Violate German Law`);
  }
  console.log(`Section ${getNextSectionNumber()}: Recommendations`);
  if (hasKeyExcerpts2) {
    console.log(`Section ${getNextSectionNumber()}: Key Excerpts from Document`);
  }
  
  // Scenario 3: No conditional sections are visible
  console.log("\nScenario 3: No conditional sections visible");
  sectionNumber = 2; // Reset after first 2 sections
  const hasSafeClauses3 = false;
  const hasAttentionClauses3 = false;
  const hasViolationClauses3 = false;
  const hasKeyExcerpts3 = false;
  
  if (hasSafeClauses3) {
    console.log(`Section ${getNextSectionNumber()}: Clauses That Are Acceptable`);
  }
  if (hasAttentionClauses3) {
    console.log(`Section ${getNextSectionNumber()}: Clauses That May Be Problematic`);
  }
  if (hasViolationClauses3) {
    console.log(`Section ${getNextSectionNumber()}: Clauses That Violate German Law`);
  }
  console.log(`Section ${getNextSectionNumber()}: Recommendations`);
  if (hasKeyExcerpts3) {
    console.log(`Section ${getNextSectionNumber()}: Key Excerpts from Document`);
  }
}

testSectionNumbering();