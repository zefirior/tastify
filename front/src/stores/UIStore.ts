import { makeAutoObservable } from 'mobx'

export type ModalType = 'none' | 'join' | 'create'

class UIStore {
  activeModal: ModalType = 'none'
  isSubmitting: boolean = false
  notification: { message: string; type: 'success' | 'error' } | null = null

  constructor() {
    makeAutoObservable(this)
  }

  openModal(modal: ModalType): void {
    this.activeModal = modal
  }

  closeModal(): void {
    this.activeModal = 'none'
  }

  setSubmitting(value: boolean): void {
    this.isSubmitting = value
  }

  showNotification(message: string, type: 'success' | 'error' = 'success'): void {
    this.notification = { message, type }
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
      this.hideNotification()
    }, 3000)
  }

  hideNotification(): void {
    this.notification = null
  }
}

export const uiStore = new UIStore()

