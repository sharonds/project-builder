// Multi-tenant database access patterns
import { db } from './firebase';

export interface Tenant {
  id: string;
  name: string;
  plan: 'free' | 'pro' | 'enterprise';
}

// Tenant-scoped collections
export const getTenantUsers = (tenantId: string) =>
  db.collection(`tenants/${tenantId}/users`);

export const getTenantProjects = (tenantId: string) =>
  db.collection(`tenants/${tenantId}/projects`);

// Data isolation by tenant
export const getUserData = async (tenantId: string, userId: string) => {
  const doc = await db.doc(`tenants/${tenantId}/users/${userId}`).get();
  return doc.data();
};
