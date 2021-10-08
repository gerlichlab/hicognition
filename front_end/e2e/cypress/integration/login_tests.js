describe('Test Login', () => {
  it('blocks login when username/password are not in db', () => {
    cy.visit("/")
    // type username
    getInputByLabel("Username").type("dummy")
    //
    getInputByLabel("Password").type("dummy")
    // click submit
    cy.contains('Submit')
      .click()
    // check that error is shown
    cy.contains("Wrong Credentials")
      .should("exist")
  });
  it('logs in user with correct username', () => {
    cy.visit("/")
    // type username
    getInputByLabel("Username").type("test")
    //
    getInputByLabel("Password").type("test")
    // click submit
    cy.contains('Submit')
      .click()
    // check whether we are on compare route
    cy.url()
      .should('be.equal', 'http://nginx/#/main/compare')
  })
  it('redirects to login when compare is visited without login', () => {
    cy.visit("/#/main/compare")
    cy.url()
      .should('be.equal', "http://nginx/#/login?redirect=%2Fmain%2Fcompare")
  })
  it('allows compare when user is logged in', () => {
    cy.visit("/")
    // type username
    getInputByLabel("Username").type("test")
    //
    getInputByLabel("Password").type("test")
    // click submit
    cy.contains('Submit')
      .click()
    cy.url()
    .should('be.equal', 'http://nginx/#/main/compare')
    // visit main page again
    cy.visit("/")
    // check whether we are on compare route
    cy.url()
    .should('be.equal', 'http://nginx/#/main/compare')
  })
})



// helper functions

const getInputByLabel = (label) => {
  return cy
    .contains('label', label)
    .invoke('attr', 'for')
    .then((id) => {
      cy.get('#' + id)
    })
}