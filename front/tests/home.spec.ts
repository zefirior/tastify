import { test, expect } from '@playwright/test'

test.describe('Home Page', () => {
  test('should display the main menu', async ({ page }) => {
    await page.goto('/')
    
    await expect(page.getByRole('heading', { name: /tastify/i })).toBeVisible()
    await expect(page.getByRole('button', { name: /create room/i })).toBeVisible()
    await expect(page.getByRole('button', { name: /join room/i })).toBeVisible()
  })

  test('should show create room form when clicking Create Room', async ({ page }) => {
    await page.goto('/')
    
    await page.getByRole('button', { name: /create room/i }).click()
    
    await expect(page.getByPlaceholder(/enter your name/i)).toBeVisible()
    await expect(page.getByRole('button', { name: /back/i })).toBeVisible()
    await expect(page.getByRole('button', { name: /create$/i })).toBeVisible()
  })

  test('should show join room form when clicking Join Room', async ({ page }) => {
    await page.goto('/')
    
    await page.getByRole('button', { name: /join room/i }).click()
    
    await expect(page.getByPlaceholder(/enter your name/i)).toBeVisible()
    await expect(page.getByPlaceholder(/abcdef/i)).toBeVisible()
    await expect(page.getByRole('button', { name: /back/i })).toBeVisible()
    await expect(page.getByRole('button', { name: /join$/i })).toBeVisible()
  })

  test('should go back to menu from create form', async ({ page }) => {
    await page.goto('/')
    
    await page.getByRole('button', { name: /create room/i }).click()
    await page.getByRole('button', { name: /back/i }).click()
    
    await expect(page.getByRole('button', { name: /create room/i })).toBeVisible()
    await expect(page.getByRole('button', { name: /join room/i })).toBeVisible()
  })

  test('should disable create button when name is empty', async ({ page }) => {
    await page.goto('/')
    
    await page.getByRole('button', { name: /create room/i }).click()
    
    const createButton = page.getByRole('button', { name: /create$/i })
    await expect(createButton).toBeDisabled()
  })

  test('should enable create button when name is filled', async ({ page }) => {
    await page.goto('/')
    
    await page.getByRole('button', { name: /create room/i }).click()
    await page.getByPlaceholder(/enter your name/i).fill('TestPlayer')
    
    const createButton = page.getByRole('button', { name: /create$/i })
    await expect(createButton).toBeEnabled()
  })
})

