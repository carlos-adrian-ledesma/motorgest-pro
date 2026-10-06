(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.MotorGestIntegrity = api;
})(typeof window !== 'undefined' ? window : globalThis, function () {
  'use strict';

  const numberValue = (value) => Number(String(value ?? 0).replace(',', '.')) || 0;

  function reverseStockForCases(state, caseIds, options = {}) {
    const ids = new Set(caseIds || []);
    if (!ids.size) return { reversedItems: 0, reversedQuantity: 0 };
    const date = options.date || new Date().toISOString().slice(0, 10);
    const createdAt = options.createdAt || new Date().toISOString();
    const idFactory = options.idFactory || ((prefix) => `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`);
    let reversedItems = 0;
    let reversedQuantity = 0;

    for (const work of state.works || []) {
      if (!ids.has(work.caseId)) continue;
      for (const part of work.stockItems || []) {
        if (part.status !== 'Utilizado') continue;
        const quantity = numberValue(part.quantity);
        if (quantity <= 0) continue;
        const item = (state.inventory || []).find((candidate) => candidate.id === part.itemId);
        if (!item) continue;
        const before = numberValue(item.stock);
        item.stock = before + quantity;
        (state.stockMovements ||= []).unshift({
          id: idFactory('MOV'),
          itemId: item.id,
          type: 'Entrada',
          quantity,
          before,
          after: numberValue(item.stock),
          date,
          reference: work.caseId,
          detail: 'Reversión automática por eliminación del diagnóstico/caso',
          reversalOfWorkId: work.id || '',
          createdAt,
        });
        reversedItems += 1;
        reversedQuantity += quantity;
      }
    }
    return { reversedItems, reversedQuantity };
  }

  function reconcileRemovedPaymentCash(state, paymentIds, options = {}) {
    const ids = new Set(paymentIds || []);
    if (!ids.size) return 0;
    const at = options.at || new Date().toISOString();
    let reconciled = 0;
    for (const movement of state.cashMovements || []) {
      if (!movement.sourcePaymentId || !ids.has(movement.sourcePaymentId)) continue;
      const oldPaymentId = movement.sourcePaymentId;
      const oldCaseId = movement.caseId || '';
      movement.status = 'Anulado';
      movement.reversedSourcePaymentId = oldPaymentId;
      movement.reversedCaseId = oldCaseId;
      movement.sourcePaymentId = '';
      movement.caseId = '';
      movement.auto = true;
      movement.reconciledAt = at;
      movement.detail = [movement.detail, `Anulado automáticamente al eliminar/revertir el pago ${oldPaymentId}.`]
        .filter(Boolean)
        .join(' ');
      reconciled += 1;
    }
    return reconciled;
  }

  function reconcileOrphanedPaymentCash(state, options = {}) {
    const validPaymentIds = new Set(
      (state.payments || []).filter((payment) => payment && payment.status === 'Confirmado').map((payment) => payment.id),
    );
    const orphanIds = (state.cashMovements || [])
      .filter((movement) => movement.sourcePaymentId && !validPaymentIds.has(movement.sourcePaymentId))
      .map((movement) => movement.sourcePaymentId);
    return reconcileRemovedPaymentCash(state, orphanIds, options);
  }

  function cashTotalsForMonth(state, month) {
    const monthRows = (state.cashMovements || []).filter((movement) => String(movement.date || '').startsWith(month));
    const confirmed = monthRows.filter((movement) => movement.status === 'Confirmado');
    const pending = monthRows.filter((movement) => movement.status === 'Pendiente');
    const sum = (rows, type) => rows.filter((movement) => movement.type === type).reduce((total, movement) => total + numberValue(movement.amount), 0);
    return {
      income: sum(confirmed, 'Ingreso'),
      expense: sum(confirmed, 'Egreso'),
      pendingIncome: sum(pending, 'Ingreso'),
      pendingExpense: sum(pending, 'Egreso'),
    };
  }

  function protectedAutomaticCashEdit(existing, submitted) {
    if (!existing || !existing.sourcePaymentId) {
      return { ...(existing || {}), ...submitted, amount: numberValue(submitted.amount) };
    }
    return {
      ...existing,
      category: submitted.category ?? existing.category,
      concept: submitted.concept ?? existing.concept,
      detail: submitted.detail ?? existing.detail,
      manualOverride: true,
    };
  }

  return {
    reverseStockForCases,
    reconcileRemovedPaymentCash,
    reconcileOrphanedPaymentCash,
    cashTotalsForMonth,
    protectedAutomaticCashEdit,
  };
});
